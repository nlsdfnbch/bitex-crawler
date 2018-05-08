"""HitBTC Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.hitbtc import HitBTCREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import HitBTCFormattedResponse
from bitex.exceptions import PairFetchError

# Init Logging Facilities
log = logging.getLogger(__name__)


class HitBTC(RESTInterface):
    """HitBtc Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(HitBTC, self).__init__('HitBTC', HitBTCREST(**api_kwargs))

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        if self.REST.version == '1':
            r = super(HitBTC, self).request('GET', 'http://api.hitbtc.com/api/2/public/symbol',
                                            endpointwithversion=True)
        else:  # default is 2
            r = super(HitBTC, self).request('GET', 'public/symbol')

        if not r.ok:
            raise PairFetchError(r.ok,r.status_code,r.reason)
        r=r.json()

        if not isinstance(r, list):
            raise PairFetchError(r)
        return [entry['id'] for entry in r]

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, verb=None, **req_kwargs):
        """Generate a request to the API."""
        verb = verb if verb else 'GET'
        if not authenticate:
            endpoint = 'public/' + endpoint
        return super(HitBTC, self).request(verb, endpoint, authenticate=authenticate,
                                           **req_kwargs)

    # Public Endpoints

    @check_and_format_pair
    @format_with(HitBTCFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        if self.REST.version == '1':
            return self.request('%s/ticker' % pair, params=kwargs)
        return self.request('ticker/%s' % pair, params=kwargs)

    @check_and_format_pair
    @format_with(HitBTCFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        if self.REST.version == '1':
            return self.request('%s/orderbook' % pair, params=kwargs)  # Version 1
        return self.request('orderbook/%s' % pair, params=kwargs)  # Version 2

    @check_and_format_pair
    @format_with(HitBTCFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        if self.REST.version == '1':
            if 'from' not in kwargs:
                return self.request('%s/trades/recent' % pair, params=kwargs)
            return self.request('%s/trades', params=kwargs)
        else:
            return self.request('trades/%s' % pair, params=kwargs)

    # Private Endpoints
    # pylint: disable=unused-argument
    def _place_order(self, pair, price, size, side, *args, **kwargs):
        """Place an order with the given parameters."""
        payload = {'symbol': pair, 'side': side, 'price': price,
                   'quantity': size, 'type': 'limit'}
        payload.update(kwargs)
        return self.request('new_order', authenticate=True, verb='POST',
                            params=kwargs)

    @check_and_format_pair
    @format_with(HitBTCFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell')

    @check_and_format_pair
    @format_with(HitBTCFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy')

    @format_with(HitBTCFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the order with given ID."""
        payload = {'client_order_id': order_id}
        payload.update(kwargs)
        return self.request('order', params=payload, authenticate=True)

    @format_with(HitBTCFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.request('orders/active', authenticate=True, params=kwargs)

    # pylint: disable=arguments-differ
    @format_with(HitBTCFormattedResponse)
    def cancel_order(self, *order_ids, cancel_all=False, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        if cancel_all:
            return self.request('cancel_orders', authenticate=True, verb='POST',
                                params=kwargs)
        results = []
        payload = kwargs
        for oid in order_ids:
            payload.update({'clientOrderId': oid})
            r = self.request('cancel_order', authenticate=True,
                             verb='POST', params=payload)
            results.append(r)
            return results if len(results) > 1 else results[0]

    @format_with(HitBTCFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        if self.REST.version == '1':
            return self.request('payment/balance', authenticate=True, params=kwargs)
        return self.request('account/balance', authenticate=True, params=kwargs)
