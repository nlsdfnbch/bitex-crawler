"""Coinnest Interface class."""
# pylint: disable=arguments-differ
# Import Built-Ins
import logging
# from bitex.exceptions import UnsupportedPairError
from bitex.api.REST.coinnest import CoinnestREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import CoinnestFormattedResponse


# Init Logging Facilities
log = logging.getLogger(__name__)


class Coinnest(RESTInterface):
    """Coinnest REST API Interface Class.

    Since Coinnest doesn't make an explicit differentiation between api versions,
    we do not use a version checker for this interface.
    """

    def __init__(self, **api_kwargs):
        """Initialize the Interface class instance."""
        super(Coinnest, self).__init__('Coinnest', CoinnestREST(**api_kwargs))

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        pairs = ["btc", "bch", "btg", "bcd", "ubtc", "btn", "kst", "ltc", "act", "eth", "etc",
                 "ada", "qtum", "xlm", "neo", "gas", "rpx", "qlc", "hsr", "knc", "tsl", "tron",
                 "omg", "wtc", "mco", "storm", "gto", "npxs", "chat", "vet", "egcc", "frec",
                 "ink", "oc", "hlc", "ent", "qbt", "spc", "put", "hotc"]
        return pairs

    def _get_supported_pairs_formatted(self):
        """Return a list of supported pairs."""
        pairs = self._get_supported_pairs()
        pairs_formatted = []
        for pair in pairs:
            pairs_formatted.append(pair.upper() + '_KRW')
        return pairs_formatted

    def request(self, endpoint, authenticate=False, **kwargs):
        """Generate a request to the API."""
        verb = 'POST' if authenticate else 'GET'
        return super(Coinnest, self).request(verb, endpoint, authenticate=authenticate, **kwargs)

    ###############
    # Basic Methods
    ###############

    # Public Endpoints

    @check_and_format_pair  # Coinnest ticker response all pairs
    @format_with(CoinnestFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for a given pair."""
        return self.request('api/pub/ticker?coin=%s' % pair, params=kwargs)

    @check_and_format_pair
    @format_with(CoinnestFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order_book for a given pair."""
        return self.request('/api/pub/depth?coin=%s' % pair, params=kwargs)

    @check_and_format_pair
    @format_with(CoinnestFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for a given pair."""
        return self.request('/api/pub/trades', params=kwargs)

    # Private Endpoints
    @check_and_format_pair
    @format_with(CoinnestFormattedResponse)
    def ask(self, pair, price, size, *args, market=False, **kwargs):
        """Place an ask order."""
        raise NotImplementedError

    @check_and_format_pair
    @format_with(CoinnestFormattedResponse)
    def bid(self, pair, price, size, *args, market=False, **kwargs):
        """Place a bid order."""
        raise NotImplementedError

    def _place_order(self, pair, price, size, side, market=None, **kwargs):
        """Place an order with the given parameters."""
        raise NotImplementedError

    @format_with(CoinnestFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status for the given order's ID."""
        raise NotImplementedError

    @format_with(CoinnestFormattedResponse)
    def open_orders(self, *args, pair=None, **kwargs):
        """Return all open orders."""
        raise NotImplementedError

    @format_with(CoinnestFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel existing order(s) with the given id(s)."""
        raise NotImplementedError

    @format_with(CoinnestFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return account's wallet."""
        return self.request('api/account/balance', authenticate=True, params=kwargs)
