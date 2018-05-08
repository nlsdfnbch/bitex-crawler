"""Exmo Interface class."""
# pylint: disable=arguments-differ
# Import Built-Ins
import logging
# from bitex.exceptions import UnsupportedPairError
from bitex.api.REST.exmo import ExmoREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import ExmoFormattedResponse
from bitex.exceptions import PairFetchError


# Init Logging Facilities
log = logging.getLogger(__name__)


class Exmo(RESTInterface):
    """Exmo REST API Interface Class.

    Since Exmo doesn't make an explicit differentiation between api versions,
    we do not use a version checker for this interface.
    """

    def __init__(self, **api_kwargs):
        """Initialize the Interface class instance."""
        super(Exmo, self).__init__('Exmo', ExmoREST(**api_kwargs))

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        r = self.request('v1/pair_settings/')
        if not r.ok:
            raise PairFetchError(r.ok,r.status_code,r.reason)

        return r.json()

    def request(self, endpoint, authenticate=False, **kwargs):
        """Generate a request to the API."""
        verb = 'POST' if authenticate else 'GET'
        return super(Exmo, self).request(verb, endpoint, authenticate=authenticate, **kwargs)

    ###############
    # Basic Methods
    ###############

    # Public Endpoints

    @check_and_format_pair  # Exmo ticker response all pairs
    @format_with(ExmoFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('v1/ticker/', params=kwargs)

    @check_and_format_pair
    @format_with(ExmoFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('v1/order_book/?pair=%s' % pair, params=kwargs)

    @check_and_format_pair
    @format_with(ExmoFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return trades for the given pair."""
        return self.request('v1/trades/?pair=%s' % pair, params=kwargs)

    # Private Endpoints
    @check_and_format_pair
    @format_with(ExmoFormattedResponse)
    def ask(self, pair, price, size, *args, market=False, **kwargs):
        """Place an ask order."""
        raise NotImplementedError

    @check_and_format_pair
    @format_with(ExmoFormattedResponse)
    def bid(self, pair, price, size, *args, market=False, **kwargs):
        """Place a bid order."""
        raise NotImplementedError

    def _place_order(self, pair, price, size, side, market=None, **kwargs):
        """Place an order with the given parameters."""
        raise NotImplementedError

    @format_with(ExmoFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status for the given order's ID."""
        raise NotImplementedError

    @format_with(ExmoFormattedResponse)
    def open_orders(self, *args, pair=None, **kwargs):
        """Return all open orders."""
        raise NotImplementedError

    @format_with(ExmoFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel existing order(s) with the given id(s)."""
        raise NotImplementedError

    @format_with(ExmoFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return account's wallet."""
        if 'pair' in kwargs:
            try:
                pair = kwargs['pair'].format_for(self.name).lower()
            except AttributeError:
                pair = kwargs['pair']

            return self.request('balance/%s/' % pair, authenticate=True, params=kwargs)
        return self.request('v1/user_info', authenticate=True, params=kwargs)

    ###########################
    # Exchange Specific Methods
    ###########################
