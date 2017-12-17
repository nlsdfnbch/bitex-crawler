"""QuadrigaCX Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.quadriga import QuadrigaCXREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class QuadrigaCX(RESTInterface):
    """QuadrigaCX Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(QuadrigaCX, self).__init__('QuadrigaCX',
                                         QuadrigaCXREST(**api_kwargs))

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if authenticate:
            return super(QuadrigaCX, self).request('POST', endpoint,
                                                   authenticate, **req_kwargs)
        return super(QuadrigaCX, self).request('GET', endpoint, authenticate,
                                               **req_kwargs)

    def _get_supported_pairs(self):
        return ['btc_cad', 'btc_usd', 'eth_btc', 'eth_cad']

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        payload = {'book': pair}
        payload.update(kwargs)
        return self.request('ticker', params=payload)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        payload = {'book': pair}
        payload.update(kwargs)
        return self.request('order_book', params=payload)

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        payload = {'book': pair}
        payload.update(kwargs)
        return self.request('transactions', params=payload)

    # Private Endpoints
    def _place_order(self, pair, price, size, side, **kwargs):
        """Place an order with the given parameters."""
        payload = {'price': price, 'amount': size, 'book': pair}
        payload.update(kwargs)
        return self.request(side, authenticate=True, params=payload)

    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell', **kwargs)

    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy', **kwargs)

    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the order with given ID."""
        payload = {'id': order_id}
        payload.update(kwargs)
        return self.request('lookup_order', authenticate=True, params=payload)

    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('open_orders', authenticate=True, params=kwargs)

    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        results = []
        payload = kwargs
        for oid in order_ids:
            payload.update({'id': oid})
            r = self.request('cancel_order', authenticate=True, params=payload)
            results.append(r)
        return results if len(results) > 1 else results[0]

    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('balance', authenticate=True, params=kwargs)
