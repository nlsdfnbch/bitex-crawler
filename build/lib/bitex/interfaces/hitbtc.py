"""
https://hitbtc.com/api
"""

# Import Built-Ins
import logging
import time
# Import Third-Party

# Import Homebrew
from bitex.api.REST import HitBTCREST
from bitex.api.WSS.hitbtc import HitBTCWSS
from bitex.utils import return_api_response
from bitex.formatters.hitbtc import HitBtcFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class HitBtc(HitBTCREST):
    def __init__(self, key='', secret='', key_file='', websocket=False):
        super(HitBtc, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)
        if websocket:
            self.wss = HitBTCWSS()
            self.wss.start()
        else:
            self.wss = None

    def public_query(self, endpoint, method_verb=None, **kwargs):
        if not method_verb:
            method_verb = 'GET'
        endpoint = 'public/' + endpoint
        return self.query(method_verb, endpoint, **kwargs)

    def private_query(self, endpoint, method_verb=None, **kwargs):
        if not method_verb:
            method_verb = 'GET'
        return self.query(method_verb, endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        q = kwargs
        return self.public_query('api/%s/orderbook' % pair, params=q)

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        q = kwargs
        if pair == 'all':
            return self.public_query('api/ticker', params=q)
        else:
            return self.public_query('api/%s/ticker' % pair, params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = kwargs
        return self.public_query('api/%s/trades' % pair, params=q)

    def _place_order(self, pair, size, price, side, order_id, **kwargs):
        q = {'symbol': pair, 'price': price, 'quantity': size, 'side': side,
             'clientOrderId': order_id}
        q.update(kwargs)
        return self.private_query('trading/new_order', method_verb='POST', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, order_id=None, **kwargs):
        order_id = order_id if order_id else str(time.time())
        self._place_order(pair, size, price, 'buy', order_id, **kwargs)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, order_id=None, **kwargs):
        order_id = order_id if order_id else str(time.time())
        self._place_order(pair, size, price, 'sell', order_id, **kwargs)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, all=False, **kwargs):
        q = {'clientOrderId': order_id}
        q.update(kwargs)
        if all:
            return self.private_query('trading/cancel_orders', params=kwargs)
        else:
            return self.private_query('trading/cancel_order', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'clientOrderId': order_id}
        q.update(kwargs)
        return self.private_query('order', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('trading/balance', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, currency=None, **kwargs):
        currency = 'BTC' if not currency else currency
        q = {'amount': size, 'currency_code': currency, 'address': tar_addr}
        q.update(kwargs)
        return self.private_query('payment/payout', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, currency=None, **kwargs):
        return self.private_query('payment/address/%s' % currency, params=kwargs)

if __name__ == ' __main__':
    k = HitBtc()
    print(k.ticker('BTCUSD'))
