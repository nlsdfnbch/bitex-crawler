"""Cryptopia Interface class."""
# Import Built-Ins
import logging

# Import third-party

# Import Homebrew
from bitex.api.REST.cryptopia import CryptopiaREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import CryptopiaFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class Cryptopia(RESTInterface):
    """Cryptopia Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Cryptopia, self).__init__('Cryptopia', CryptopiaREST(**api_kwargs))

    def _get_supported_pairs(self):
        r = self.request('GetTradePairs/').json()
        pairs = [entry['Label'].replace('/', '_') for entry in r['Data']]
        return pairs

    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Query the API and return its result."""
        if authenticate:
            return super(Cryptopia, self).request('POST', endpoint, authenticate=authenticate,
                                                  **req_kwargs)
        return super(Cryptopia, self).request('GET', endpoint, authenticate=authenticate,
                                              **req_kwargs)

    # Public Endpoints

    @check_and_format_pair
    @format_with(CryptopiaFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('GetMarket/' + pair, params=kwargs)

    @check_and_format_pair
    @format_with(CryptopiaFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return self.request('GetMarketOrders/' + pair, params=kwargs)

    @check_and_format_pair
    @format_with(CryptopiaFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        return self.request('GetMarketHistory/' + pair, params=kwargs)

    # Private Endpoints
    # pylint: disable=unused-argument
    def _place_order(self, pair, price, size, side, *args, **kwargs):
        """Place an order with the given parameters."""
        payload = {'Market': pair, 'Type': side, 'Rate': price, 'Amount': size}
        payload.update(kwargs)
        return self.request('SubmitTrade', params=payload, authenticate=True)

    @check_and_format_pair
    @format_with(CryptopiaFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'Sell', *args, **kwargs)

    @check_and_format_pair
    @format_with(CryptopiaFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'Buy', *args, **kwargs)

    @format_with(CryptopiaFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the order with given ID."""
        raise NotImplementedError

    @format_with(CryptopiaFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('GetOpenOrders', params=kwargs, authenticate=True)

    @format_with(CryptopiaFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        results = []
        payload = {'Type': 'Trade'}
        for oid in order_ids:
            payload.update({'OrderId': oid})
            r = self.request('CancelTrade', params=payload,
                             authenticate=True)
            results.append(r)
        return results if len(results) > 1 else results[0]

    @format_with(CryptopiaFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('GetBalance', params=kwargs, authenticate=True)
