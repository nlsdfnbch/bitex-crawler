"""CEX.IO Interface class."""
# Import Built-Ins
import logging

# Import Third-party

# Import Homebrew
from bitex.api.REST.cexio import CEXioREST

from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import CEXioFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class CEXio(RESTInterface):
    """CEXio REST API Interface Class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        # if 'key' in api_kwargs: key = api_kwargs['key']
        super(CEXio, self).__init__('CEXio', CEXioREST(**api_kwargs))

    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if not authenticate:
            return super(CEXio, self).request('GET', endpoint, authenticate=authenticate,
                                              **req_kwargs)
        return super(CEXio, self).request('POST', endpoint, authenticate=authenticate, **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        r = self.request('currency_limits').json()
        pairs = [item['symbol1'] + item['symbol2'] for item in r['data']['pairs']]
        return pairs

    ###############
    # Basic Methods
    ###############
    @format_with(CEXioFormattedResponse)
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('ticker/{}/{}'.format(pair[:-3], pair[-3:]))

    @check_and_format_pair
    @format_with(CEXioFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for a given pair."""
        return self.request('order_book/{}/{}'.format(pair[:-3], pair[-3:]))

    @check_and_format_pair
    @format_with(CEXioFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        return self.request('trade_history/{}/{}'.format(pair[:-3], pair[-3:]))

    # Private Endpoints
    @check_and_format_pair
    @format_with(CEXioFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        raise NotImplementedError

    @check_and_format_pair
    @format_with(CEXioFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        raise NotImplementedError

    @format_with(CEXioFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return order status of order with given id."""
        raise NotImplementedError

    @format_with(CEXioFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        raise NotImplementedError

    @format_with(CEXioFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with given ID(s)."""
        raise NotImplementedError

    @format_with(CEXioFormattedResponse)
    def wallet(self, *args, currency=None, **kwargs):  # pylint: disable=arguments-differ
        """Return the account wallet."""
        payload = kwargs
        return self.request('balance/', params=payload, authenticate=True)

        ###########################
        # Exchange Specific Methods
        ###########################
