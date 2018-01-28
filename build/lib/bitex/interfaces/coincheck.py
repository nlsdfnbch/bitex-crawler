"""
https://coincheck.com/documents/exchange/api
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import CoincheckREST
from bitex.utils import return_api_response
from bitex.formatters.coincheck import CnckFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class Coincheck(CoincheckREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Coincheck, self).__init__(key, secret)
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
        return self.public_query('ticker', params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('trades', params=q)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        q = {'pair': pair}
        q.update(kwargs)
        return self.public_query('order_books', params={'pair': pair})

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'rate': price, 'amount': size, 'pair': pair,
             'order_type': 'buy'}
        q.update(kwargs)
        return self.private_query('orders', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'rate': price, 'amount': size, 'pair': pair,
             'order_type': 'sell'}
        q.update(kwargs)
        return self.private_query('orders', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        return self.private_query('exchange/orders/%s' % order_id, params=kwargs)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        raise NotImplementedError()

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('accounts/balance')

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'address': tar_addr, 'amount': size}
        q.update(kwargs)
        return self.private_query('send_money', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError()

    """
    Exchange Specific Methods
    """
