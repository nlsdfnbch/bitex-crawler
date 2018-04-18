"""Binance Interface class."""
# Import Built-Ins
import logging
from bitex.api.REST.binance import BinanceREST
from bitex.interface.rest import RESTInterface
from bitex.utils import format_with, check_and_format_pair
from bitex.formatters import BinanceFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class Binance(RESTInterface):
    """Binance Interface class.

    Includes standardized methods, as well as all other Endpoints
    available on their REST API.
    """

    # pylint: disable=arguments-differ

    def __init__(self, **api_kwargs):
        """Initialize class instance."""
        super(Binance, self).__init__('Binance', BinanceREST(**api_kwargs))

    def request(self, verb, endpoint, authenticate=False, **req_kwargs):
        """Preprocess request to API."""
        return super(Binance, self).request(verb, endpoint, authenticate=authenticate,
                                            **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        r = self.request('GET', 'v1/exchangeInfo')
        r = r.json()
        pairs = [entry['symbol'] for entry in r['symbols']]
        return pairs

    def _get_supported_pairs_formatted(self):
        """Return a list of supported pairs."""
        pairs = self._supported_pairs
        pairs_formatted = []
        for pair in pairs:
            if pair[-4:] == 'USDT':
                base = pair[:-4]
                quote = 'USDT'
            else:
                base = pair[:-3]
                quote = pair[-3:]
            pairs_formatted.append((base + '_' + quote).upper())
        return pairs_formatted

    @check_and_format_pair
    @format_with(BinanceFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        payload = {'symbol': pair}
        payload.update(kwargs)
        return self.request('GET', 'v1/ticker/24hr', params=payload)

    @check_and_format_pair
    @format_with(BinanceFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        payload = {'symbol': pair}
        payload.update(kwargs)
        return self.request("GET", "v1/depth", params=payload)

    @check_and_format_pair
    @format_with(BinanceFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        payload = {'symbol': pair}
        payload.update(kwargs)
        return self.request('GET', 'v1/trades', params=payload)

    # Private Endpoints
    # pylint: disable=unused-argument
    def _place_order(self, pair, price, size, side, *args, **kwargs):
        payload = {'symbol': pair,
                   'side': side,
                   'type': "LIMIT_MAKER",
                   'price': price,
                   'quantity': size}
        payload.update(kwargs)
        return self.request('POST', 'v3/order', authenticate=True, params=payload)

    @check_and_format_pair
    @format_with(BinanceFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, "SELL", *args, **kwargs)

    @check_and_format_pair
    @format_with(BinanceFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, "BUY", *args, **kwargs)

    @format_with(BinanceFormattedResponse)
    def order_status(self, order_id, pair, *args, **kwargs):
        """Return the status of an order with the given id."""
        payload = {'symbol': pair,
                   'orderId': order_id}
        payload.update(kwargs)
        return self.request('GET', 'v3/order', authenticate=True, params=payload)

    @format_with(BinanceFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('GET', 'v3/openOrders', authenticate=True, params=kwargs)

    @format_with(BinanceFormattedResponse)
    def cancel_order(self, *order_ids, pair, **kwargs):
        """Cancel the order(s) with the given id(s)."""
        results = []
        for order_id in order_ids:
            payload = {'symbol': pair,
                       'orderId': order_id}
            payload.update(kwargs)
            r = self.request('DELETE', 'v3/order', authenticate=True, params=payload)
            results.append(r)
        return results if len(results) > 1 else results[0]

    @format_with(BinanceFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return the wallet of this account."""
        return self.request('GET', "v3/account", True)
