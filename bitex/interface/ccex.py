"""C-CEX Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.ccex import CCEXREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import CCEXFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class CCEX(RESTInterface):
    """C-CEX Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(CCEX, self).__init__('C-CEX', CCEXREST(**api_kwargs))

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if authenticate:
            endpoint = endpoint if endpoint else 'api.html'
        else:
            endpoint = endpoint if endpoint else 'api_pub.html'
        return super(CCEX, self).request('GET', endpoint, authenticate=authenticate, **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        return self.request('/pairs.json').json()['pairs']

    # Public Endpoints

    @check_and_format_pair
    @format_with(CCEXFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('{}.json'.format(pair), params=kwargs)

    @check_and_format_pair
    @format_with(CCEXFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        payload = {'a': 'getorderbook', 'market': pair, 'type': 'both'}
        payload.update(kwargs)
        return self.request(None, params=payload)

    @check_and_format_pair
    @format_with(CCEXFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        payload = {'a': 'getmarkethistory', 'market': pair}
        payload.update(kwargs)
        return self.request(None, params=payload)

    # Private Endpoints
    @check_and_format_pair
    @format_with(CCEXFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        payload = {'a': 'selllimit', 'market': pair, 'quantity': size, 'rate': price}
        payload.update(kwargs)
        return self.request(None, authenticate=True, params=payload)

    @check_and_format_pair
    @format_with(CCEXFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        payload = {'a': 'buylimit', 'market': pair, 'quantity': size, 'rate': price}
        payload.update(kwargs)
        return self.request(None, authenticate=True, params=payload)

    @format_with(CCEXFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the given order ID."""
        payload = {'a': 'getorder', 'uuid': order_id}
        payload.update(kwargs)
        return self.request(None, params=payload, authenticate=True)

    @format_with(CCEXFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        payload = {'a': 'getopenorders'}
        payload.update(kwargs)
        return self.request(None, params=payload, authenticate=True)

    @format_with(CCEXFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel the order(s) with the given order ID(s)."""
        payload = {'a': 'cancel'}
        payload.update(kwargs)
        results = []
        for oid in order_ids:
            payload.update({'uuid': oid})
            results.append(self.request(None, params=payload, authenticate=True))
        return results if len(results) > 1 else results[0]

    @format_with(CCEXFormattedResponse)
    def wallet(self, *args, currency=None, **kwargs):
        """Return the account's wallet."""
        if currency:
            payload = {'a': 'getbalance'}
            payload.update(kwargs)
            payload.update({'currency': currency})
        else:
            payload = {'a': 'getbalances'}
            payload.update(kwargs)
        return self.request(None, params=payload, authenticate=True)
