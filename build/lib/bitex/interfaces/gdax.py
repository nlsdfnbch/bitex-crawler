"""
https://docs.gdax.com/
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import GDAXRest
from bitex.api.WSS.gdax import GDAXWSS
from bitex.utils import return_api_response
from bitex.formatters.gdax import GdaxFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class GDAX(GDAXRest):
    def __init__(self, key='', secret='', key_file='', websocket=False):
        super(GDAX, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)
        if websocket:
            self.wss = GDAXWSS()
            self.wss.start()
        else:
            self.wss = None

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, method_verb='POST', **kwargs):
        return self.query(method_verb, endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        return self.public_query('products/%s/ticker' % pair, params=kwargs)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        return self.public_query('products/%s/book' % pair, params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        return self.public_query('products/%s/trades' % pair, params=kwargs)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'side': 'buy', 'type': 'market', 'product_id': pair,
             'price': price, 'size': size}
        q.update(kwargs)
        return self.private_query('orders', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'side': 'sell', 'type': 'market', 'product_id': pair,
             'price': price, 'size': size}
        q.update(kwargs)
        return self.private_query('orders', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, all=False, **kwargs):

        if not all:
            return self.private_query('orders/%s' % order_id,
                                      method_verb='DELETE', params=kwargs)
        else:
            return self.private_query('orders', method_verb='DELETE',
                                      params=kwargs)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        return self.private_query('orders/%s' % order_id, method_verb='GET',
                                  params=kwargs)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('accounts', method_verb='GET', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        raise NotImplementedError()

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError()

    """
    Exchange Specific Methods
    """

    @return_api_response
    def time(self):
        return self.public_query('time')

    @return_api_response(None)
    def currencies(self):
        return self.public_query('currencies')

    @return_api_response(None)
    def pairs(self):
        return self.public_query('products')

    @return_api_response(None)
    def ohlc(self, pair, **kwargs):
        return self.public_query('products/%s/candles' % pair, params=kwargs)

    @return_api_response(None)
    def stats(self, pair, **kwargs):
        return self.public_query('products/%s/stats' % pair, params=kwargs)
