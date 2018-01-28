"""
https://www.okcoin.com/about/rest_api.do
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import OKCoinREST
from bitex.utils import return_api_response
from bitex.formatters.okcoin import OkcnFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class OKCoin(OKCoinREST):
    def __init__(self, key='', secret='', key_file=''):
        super(OKCoin, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, **kwargs):
        return self.query('POST', endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """
    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('ticker.do', params=q)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('depth.do', params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('trades.do', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'symbol': pair, 'price': price, 'amount': size, 'type': 'buy'}
        q.update(kwargs)
        return self.private_query('trade.do', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'symbol': pair, 'price': price, 'amount': size, 'type': 'sell'}
        q.update(kwargs)
        return self.private_query('trade.do', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        q = {'order_id': order_id}
        q.update(kwargs)
        return self.private_query('cancel_order.do', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'order_id': order_id}
        q.update(kwargs)
        return self.private_query('orders.info', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('userinfo.do', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'withdraw_address': tar_addr, 'withdraw_amount': size}
        q.update(kwargs)
        return self.private_query('withdraw.do', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError()

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def ohlc(self, pair):
        return self.public_query('kline.do', params={'pair': pair})

    @return_api_response(None)
    def future_ticker(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_ticker.do', params=q)

    @return_api_response(None)
    def future_order_book(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_order_book.do', params=q)

    @return_api_response(None)
    def future_trades(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_trades.do', params=q)

    @return_api_response(None)
    def future_index(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_index.do', params=q)

    @return_api_response(None)
    def usd_cny_rate(self):
        return self.public_query('exchange_rate.do', params=q)

    @return_api_response(None)
    def future_estimate(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_estimated_price.do', params=q)

    @return_api_response(None)
    def future_ohlc(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_kline.do', params=q)

    @return_api_response(None)
    def future_holds(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_hold_amount.do', params=q)

    @return_api_response(None)
    def future_limit_price(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('future_price_limit.do', params=q)

    @return_api_response(None)
    def otc_order_book(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('otcs.do', params=q)
