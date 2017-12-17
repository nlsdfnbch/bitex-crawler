"""Vaultoro Interface class."""
# Import Built-Ins
import logging
import time

# Import Homebrew
from bitex.api.REST.vaultoro import VaultoroREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class Vaultoro(RESTInterface):
    """Vaultoro Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Vaultoro, self).__init__('Vaultoro', VaultoroREST(**api_kwargs))

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, post=False, **req_kwargs):
        """Generate a request to the API."""
        verb = 'GET' if not post else 'POST'
        endpoint = '1/' + endpoint if authenticate else endpoint
        return super(Vaultoro, self).request(verb, endpoint, authenticate,
                                             **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        return ['BTC-GLD']

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('markets', params=kwargs)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('orderbook/', params=kwargs)

    # pylint: disable=arguments-differ
    @check_and_format_pair
    def trades(self, pair, *args, since=None, **kwargs):
        """Return the trades for the given pair."""
        q = {'since': time.time() - 360 if not since else since}
        q.update(kwargs)
        return self.request('latesttrades', params=q)

    # Private Endpoints
    # pylint: disable=unused-argument
    def _place_order(self, pair, price, size, side, market_order, **kwargs):
        """Place an order with the given parameters."""
        order_type = 'limit' if not market_order else 'market'
        q = {'gld': size, 'price': price}
        return self.request('%s/gld/%s' %
                            (side, order_type), authenticate=True,
                            post=True, params=q)

    # pylint: disable=arguments-differ
    @check_and_format_pair
    def ask(self, pair, price, size, *args, market_order=False, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell', market_order,
                                 **kwargs)

    # pylint: disable=arguments-differ
    @check_and_format_pair
    def bid(self, pair, price, size, *args, market_order=False, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy', market_order,
                                 **kwargs)

    def order_status(self, order_id, *args, **kwargs):
        """Return the status of the order with the given order ID."""
        raise NotImplementedError

    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('orders',
                            authenticate=True, params=kwargs)

    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with the given order ID(s)."""
        results = []
        for oid in order_ids:
            r = self.request('cancel/%s' % oid,
                             authenticate=True, post=True, params=kwargs)
            results.append(r)
        return results if len(results) > 1 else results[0]

    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('balance',
                            authenticate=True, params=kwargs)
