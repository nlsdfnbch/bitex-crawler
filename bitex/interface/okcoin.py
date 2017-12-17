"""OKCoin Interface class."""
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.okcoin import OKCoinREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class OKCoin(RESTInterface):
    """OKCoin Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(OKCoin, self).__init__('OKCoin', OKCoinREST(**api_kwargs))

    # pylint: disable=arguments-differ
    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if authenticate:
            return super(OKCoin, self).request('POST', endpoint, authenticate,
                                               **req_kwargs)
        return super(OKCoin, self).request('GET', endpoint, authenticate,
                                           **req_kwargs)

    def _get_supported_pairs(self):
        return ['btc_usd', 'ltc_usd', 'eth_usd',
                'btc_cny', 'ltc_cny', 'eth_cny']

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        payload = {'symbol': pair}
        payload.update(kwargs)
        return self.request('ticker.do', params=payload)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        payload = {'symbol': pair}
        payload.update(kwargs)
        return self.request('depth.do', params=payload)

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        """Return the trades for the given pair."""
        payload = {'symbol': pair}
        payload.update(kwargs)
        return self.request('trades.do', params=payload)

    # Private Endpoints
    def _place_order(self, pair, price, size, side, **kwargs):
        """Place an order with the given parameters."""
        payload = {'symbol': pair, 'type': side,
                   'price': price, 'amount': size}
        payload.update(kwargs)
        return self.request('trade.do', authenticate=True, params=payload)

    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell')

    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy')

    def order_status(self, order_id, *args, **kwargs):
        """Return the order status of the order with given ID."""
        payload = {'order_id': order_id}
        payload.update(kwargs)
        return self.request('order_info.do', authenticate=True, params=payload)

    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.order_status(-1, **kwargs)

    def cancel_order(self, *order_ids, **kwargs):
        """Cancel order(s) with the given ID(s)."""
        payload = kwargs
        payload.update({'order_id': ','.join(list(order_ids))})
        return self.request('cancel_order.do', authenticate=True,
                            params=payload)

    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.request('userinfo.do', authenticate=True, params=kwargs)
