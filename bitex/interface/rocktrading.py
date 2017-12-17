"""The Rock Trading Ltd Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.rocktrading import RockTradingREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class TheRockTrading(RESTInterface):
    """The Rock Trading Ltd Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(TheRockTrading, self).__init__('The Rock Trading Ltd.',
                                             RockTradingREST(**api_kwargs))

    def _get_supported_pairs(self):
        """Return a list of all supported pairs."""
        return [d['id'] for d in self.request('GET', 'funds').json()['funds']]

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('GET', 'funds/%s/ticker' % pair, params=kwargs)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('GET', 'funds/%s/orderbook' % pair, params=kwargs)

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        return self.request('GET', 'funds/%s/trades' % pair, params=kwargs)

    # Private Endpoints
    def _place_order(self, pair, price, size, side, **kwargs):
        """Place an order with the given parameters."""
        payload = {'price': price, 'amount': size, 'side': side}
        payload.update(kwargs)
        return self.request('POST', 'funds/%s/orders' % pair,
                            authenticate=True, params=payload)

    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell', **kwargs)

    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy', **kwargs)

    def order_status(self, order_id, *args, **kwargs):
        """Return the status of the order with the given ID."""
        if 'pair' not in kwargs and 'fund_id' not in kwargs:
            raise ValueError("Need to specify pair or fund_id in kwargs!")
        try:
            pair = kwargs.pop('pair')
        except KeyError:
            pair = kwargs.pop('fund_id')
        return self.request('GET', 'funds/%s/orders/%s' % (pair, order_id),
                            authenticate=True, params=kwargs)

    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        if 'pair' not in kwargs and 'fund_id' not in kwargs:
            results = []
            for fund_id in self.supported_pairs:
                r = self.request('GET', 'funds/%s/orders' % fund_id,
                                 authenticate=True, params=kwargs)
                results.append(r)
            return results if len(results) > 1 else results[0]
        try:
            pair = kwargs.pop('pair')
        except KeyError:
            pair = kwargs.pop('fund_id')

        return self.request('GET', 'funds/%s/orders' % pair,
                            authenticate=True, params=kwargs)

    # pylint: disable=arguments-differ
    def cancel_order(self, *order_ids, all_orders=False, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        results = []
        if 'pair' not in kwargs and 'fund_id' not in kwargs:
            for fund_id in self.supported_pairs:
                r = self.cancel_order(*order_ids, all_orders, pair=fund_id)
                results.append(r)
            return results if len(results) > 1 else results[0]
        else:
            try:
                pair = kwargs.pop('pair')
            except KeyboardInterrupt:
                pair = kwargs.pop('fund_id')
        if all_orders:
            return self.request('DELETE', 'funds/%s/orders/remove_all' % pair,
                                authenticate=True, params=kwargs)
        for oid in order_ids:
            r = self.request('DELETE', 'funds/%s/orders/%s' % (pair, oid),
                             authenticate=True, params=kwargs)
            results.append(r)
        return results if len(results) > 1 else results[0]

    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('GET', 'balances', authenticate=True,
                            params=kwargs)
