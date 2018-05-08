"""CoinOne Interface class."""
# Import Built-Ins
import logging
from bitex.api.REST.coinone import CoinoneREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import CoinoneFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class Coinone(RESTInterface):
    """Coinone REST API Interface Class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        # if 'key' in api_kwargs: key = api_kwargs['key']
        super(Coinone, self).__init__('Coinone', CoinoneREST(**api_kwargs))

    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        method = 'POST' if authenticate else 'GET'
        return super(Coinone, self).request(method, endpoint, authenticate=authenticate,
                                            **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs, CoinOne just support KRW."""
        pairs = ["btc", "bch", "eth", "etc", "xrp", "qtum", "iota", "ltc", "btg"]
        return pairs

    def _get_supported_pairs_formatted(self):
        """Return a list of supported pairs."""
        pairs = self._supported_pairs
        pairs_formatted = []
        for pair in pairs:
            pairs_formatted.append(pair.upper() + '_KRW')
        return pairs_formatted

    ###############
    # Basic Methods
    ###############
    @format_with(CoinoneFormattedResponse)
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('ticker?currency={}'.format(pair))

    @check_and_format_pair
    @format_with(CoinoneFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('orderbook?currency={}'.format(pair))
        # payload = {'currency': pair}
        # payload.update(kwargs)
        # return self.request('orderbook', params=payload)

    @check_and_format_pair
    @format_with(CoinoneFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        return self.request('trades')

    # Private Endpoints
    @check_and_format_pair
    @format_with(CoinoneFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        raise NotImplementedError

    @check_and_format_pair
    @format_with(CoinoneFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        raise NotImplementedError

    @format_with(CoinoneFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return order status of order with given id."""
        raise NotImplementedError

    @format_with(CoinoneFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        raise NotImplementedError

    @format_with(CoinoneFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with given ID(s)."""
        raise NotImplementedError

    @format_with(CoinoneFormattedResponse)
    def wallet(self, *args, currency=None, **kwargs):  # pylint: disable=arguments-differ
        """Return the account wallet."""
        payload = kwargs
        payload['access_token'] = self.REST.key
        return self.request('v2/account/balance/', params=payload, authenticate=True)

        ###########################
        # Exchange Specific Methods
        ###########################
