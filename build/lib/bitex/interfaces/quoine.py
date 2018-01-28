"""
https://developers.quoine.com/
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import QuoineREST
from bitex.utils import return_api_response
from bitex.formatters.quoine import QoinFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class Quoine(QuoineREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Quoine, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

        self.pairs = {d['currency_pair_code']: d['id']
                      for d in self.public_query('products').json()}

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, method='POST', **kwargs):
        return self.query(method, endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        pair = self.pairs[pair]
        return self.public_query('products/%s' % pair, params=kwargs)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        pair = self.pairs[pair]
        return self.public_query('products/%s/price_levels' % pair, params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = {'currency_pair_code': pair}
        q.update(kwargs)
        return self.public_query('executions/', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'quantity': size, 'price': price, 'order_type': 'limit',
             'product_id': self.pairs[pair], 'side': 'buy'}
        q.update(kwargs)
        return self.private_query('orders', params={'order': q})

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'quantity': size, 'price': price, 'order_type': 'limit',
             'product_id': self.pairs[pair], 'side': 'sell'}
        q.update(kwargs)
        return self.private_query('orders', params={'order': q})

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        return self.private_query('orders/%s/cancel' % order_id,
                                  method='PUT')

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        return self.private_query('orders/%s' % order_id, method='GET')

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('/accounts/balance/', method='GET')

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        raise NotImplementedError()

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError()

    """
    Exchange Specific Methods
    """
