"""Poloniex Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.poloniex import PoloniexREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import PoloniexFormattedResponse
from bitex.exceptions import PairFetchError

# Init Logging Facilities
log = logging.getLogger(__name__)


class Poloniex(RESTInterface):
    """Poloniex Interface class.

    Includes standardized methods, as well as all other Endpoints
    available on their REST API.
    """

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Poloniex, self).__init__('Poloniex', PoloniexREST(**api_kwargs))

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if 'params' in req_kwargs:
            req_kwargs['params'].update({'command': endpoint})
        else:
            req_kwargs['params'] = {'command': endpoint}
        if authenticate:
            return super(Poloniex, self).request(
                'POST', endpoint, authenticate=True, **req_kwargs)
        return super(Poloniex, self).request(
            'GET', 'public', authenticate=False, **req_kwargs)

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        # Retrieve the pairs through a call to the public ticker endpoint.
        # Can't call self.ticker, because it looks up the pair in this method.
        r = self.request("returnTicker")
        if not r.ok:
            raise PairFetchError(r.ok,r.status_code,r.reason)

        return list(r.json().keys())

    def _get_supported_pairs_formatted(self):
        """Return a list of supported pairs."""
        pairs = self._supported_pairs
        pairs_formatted = []
        for pair in pairs:
            base, quote = pair.split('_')

            if ((base == 'BTC') or (base == 'USDT') or
                    (base == 'XMR' and not (quote == 'BTC' or quote == 'USDT'))):
                pair = quote + '_' + base
            else:
                pair = base + '_' + quote
            pairs_formatted.append(pair)
        return pairs_formatted

    # Public Endpoints

    @check_and_format_pair
    @format_with(PoloniexFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return self.request('returnTicker', params=kwargs)

    @check_and_format_pair
    @format_with(PoloniexFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        payload = {'currencyPair': pair}
        payload.update(kwargs)
        return self.request('returnOrderBook', params=payload)

    @check_and_format_pair
    @format_with(PoloniexFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        payload = {'currencyPair': pair}
        payload.update(kwargs)
        return self.request('returnTradeHistory', params=payload)

    # Private Endpoints
    def _place_order(self, pair, price, size, side, **kwargs):
        """Place an order with the given parameters."""
        payload = {'currencyPair': pair, 'rate': price, 'amount': size}
        payload.update(kwargs)
        if side == 'buy':
            return self.request('buy', authenticate=True, params=payload)
        return self.request('sell', authenticate=True, params=payload)

    @check_and_format_pair
    @format_with(PoloniexFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        raise NotImplementedError

    @check_and_format_pair
    @format_with(PoloniexFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        raise NotImplementedError

    @format_with(PoloniexFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the order with given ID."""
        payload = {'orderNumber': order_id}
        payload.update(kwargs)
        return self.request('returnOrderTrades', authenticate=True, params=payload)

    @format_with(PoloniexFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        payload = {'currencyPair': 'all'}
        payload.update(kwargs)
        return self.request('returnOpenOrders', authenticate=True, params=payload)

    @format_with(PoloniexFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        results = []
        payload = kwargs or {}
        for oid in order_ids:
            payload.update({'orderNumber': oid})
            r = self.request('cancelOrder', authenticate=True, params=payload)
            results.append(r)
        return results if len(results) > 1 else results[0]

    @format_with(PoloniexFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('returnTradableBalances', authenticate=True, params=kwargs)
