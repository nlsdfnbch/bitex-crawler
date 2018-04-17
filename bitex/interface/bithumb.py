"""Bitstamp Interface class."""
# Import Built-Ins
import logging
from bitex.api.REST.bithumb import BithumbREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import BithumbFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class Bithumb(RESTInterface):
    """Bithumb REST API Interface Class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Bithumb, self).__init__('Bithumb', BithumbREST(**api_kwargs))

    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if not authenticate:
            return super(Bithumb, self).request('GET', endpoint, authenticate=authenticate,
                                                **req_kwargs)
        return super(Bithumb, self).request('POST', endpoint, authenticate=authenticate,
                                            **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        pairs = ['BTC', 'ETH', 'DASH', 'LTC', 'ETC', 'XRP', 'BCH', 'XMR', 'ZEC', 'QTUM', 'BTG',
                 'EOS']
        return pairs

    def _get_supported_pairs_formatted(self):
        """Return a list of supported pairs."""
        pairs = self._get_supported_pairs()
        pairs_formatted = []
        for pair in pairs:
            pairs_formatted.append(pair.upper() + '_KRW')
        return pairs_formatted

    ###############
    # Basic Methods
    ###############
    @format_with(BithumbFormattedResponse)
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for a given pair."""
        return self.request('public/ticker/%s' % pair)

    @check_and_format_pair
    @format_with(BithumbFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order_book for a given pair."""
        return self.request('public/orderbook/%s' % pair)

    @check_and_format_pair
    @format_with(BithumbFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        return self.request('public/recent_transactions/%s' % pair)

    # Private Endpoints
    @check_and_format_pair
    @format_with(BithumbFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        raise NotImplementedError

    @check_and_format_pair
    @format_with(BithumbFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        raise NotImplementedError

    @format_with(BithumbFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return order status of order with given id."""
        raise NotImplementedError

    @format_with(BithumbFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        raise NotImplementedError

    @format_with(BithumbFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with given ID(s)."""
        raise NotImplementedError

    @format_with(BithumbFormattedResponse)
    def wallet(self, *args, currency=None, **kwargs):  # pylint: disable=arguments-differ
        """Return the account wallet."""
        if currency:
            payload = {'currency': currency}
            payload.update(kwargs)
            return self.request('info/balance', params=payload, authenticate=True)
        payload = kwargs
        return self.request('info/balance', params=payload, authenticate=True)

    ###########################
    # Exchange Specific Methods
    ###########################
