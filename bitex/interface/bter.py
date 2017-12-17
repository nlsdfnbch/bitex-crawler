"""Bter Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.bter import BterREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class Bter(RESTInterface):
    """Bter Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Bter, self).__init__('Bter', BterREST(**api_kwargs))

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        return self.request('GET', 'pairs').json()

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for given pair."""
        return self.request('GET', 'ticker/%s' % pair)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('GET', 'orderBook/%s' % pair)

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        tid = '' if 'TID' not in kwargs else '/' + str(kwargs['TID'])
        return self.request('GET', 'tradeHistory' + tid)

    # Private Endpoints
    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_orde(pair, price, size, 'sell', **kwargs)

    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_orde(pair, price, size, 'buy', **kwargs)

    def _place_orde(self, pair, price, size, side, **kwargs):
        """Place an order with the given parameters."""
        payload = {'currencyPair': pair, 'rate': price, 'amount': size}
        payload.update(kwargs)
        return self.request('POST', 'private/%s' % side, authenticate=True,
                            params=payload)

    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the given order ID."""
        payload = {'orderNumber': order_id}
        payload.update(kwargs)
        return self.request('POST', 'private/getOrder', params=payload,
                            authenticate=True)

    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('POST', 'private/openOrders', authenticate=True)

    # pylint: disable=arguments-differ
    def cancel_order(self, *order_ids, cancel_all=False, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        if cancel_all:
            return self.request('POST', 'private/cancelAllOrders',
                                params=kwargs, authenticate=True)
        results = []
        payload = kwargs
        for oid in order_ids:
            payload.update({'orderNumber': oid})
            results.append(self.request('POST', 'private/cancelOrder',
                                        params=payload, authenticate=True))
        return results if len(results) > 1 else results[0]

    def wallet(self, *args, **kwargs):
        """Return the wallet of the account."""
        return self.request('POST', 'private/balances', authenticate=True)
