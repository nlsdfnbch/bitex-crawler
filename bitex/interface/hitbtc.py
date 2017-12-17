"""HitBTC Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.hitbtc import HitBTCREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class HitBTC(RESTInterface):
    """HitBtc Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(HitBTC, self).__init__('HitBTC', HitBTCREST(**api_kwargs))

    def _get_supported_pairs(self):
        r = self.request('symbols')
        return [entry['symbol'] for entry in r.json()['symbols']]

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, verb=None, **req_kwargs):
        """Generate a request to the API."""
        verb = verb if verb else 'GET'
        if authenticate:
            endpoint = 'trading/' + endpoint
        else:
            endpoint = 'public/' + endpoint
        return super(HitBTC, self).request(verb, endpoint, authenticate,
                                           **req_kwargs)

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('%s/ticker' % pair, params=kwargs)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('%s/orderbook' % pair, params=kwargs)

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        if 'from' not in kwargs:
            return self.request('%s/trades/recent' % pair, params=kwargs)
        return self.request('%s/trades', params=kwargs)

    # Private Endpoints
    # pylint: disable=unused-argument
    def _place_order(self, pair, price, size, side, *args, **kwargs):
        """Place an order with the given parameters."""
        payload = {'symbol': pair, 'side': side, 'price': price,
                   'quantity': size, 'type': 'limit'}
        payload.update(kwargs)
        return self.request('new_order', authenticate=True, verb='POST',
                            params=kwargs)

    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell')

    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy')

    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the order with given ID."""
        payload = {'client_order_id': order_id}
        payload.update(kwargs)
        return self.request('order', params=payload, authenticate=True)

    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('orders/active', authenticate=True, params=kwargs)

    # pylint: disable=arguments-differ
    def cancel_order(self, *order_ids, cancel_all=False, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        if cancel_all:
            return self.request('cancel_orders', authenticate=True,
                                verb='POST', params=kwargs)
        results = []
        payload = kwargs
        for oid in order_ids:
            payload.update({'clientOrderId': oid})
            r = self.request('cancel_order', authenticate=True,
                             verb='POST', params=payload)
            results.append(r)
            return results if len(results) > 1 else results[0]

    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('balance', authenticate=True, params=kwargs)
