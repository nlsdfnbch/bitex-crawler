"""
https://www.quadrigacx.com/api_info
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import QuadrigaCXREST
from bitex.utils import return_api_response
from bitex.formatters.quadriga import QuadrigaCXFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class QuadrigaCX(QuadrigaCXREST):
    def __init__(self, key='', secret='', key_file=''):
        super(QuadrigaCX, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, method='POST', **kwargs):
        return self.query(method, endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        q = {'book': pair}
        q.update(kwargs)
        return self.public_query('ticker', params=q)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        q = {'book': pair}
        q.update(kwargs)
        return self.public_query('order_book', params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = {'book': pair}
        q.update(kwargs)
        return self.public_query('transactions', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'amount': size, 'price': price, 'book': pair}
        q.update(kwargs)
        return self.private_query('buy', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'amount': size, 'price': price, 'book': pair}
        q.update(kwargs)
        return self.private_query('sell', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        q = {'id': order_id}
        q.update(kwargs)
        return self.private_query('cancel_order', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'id': order_id}
        q.update(kwargs)
        return self.private_query('lookup_order', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('balance', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, cur='bitcoin', **kwargs):
        q = {'amount': size, 'address': tar_addr}
        q.update(kwargs)
        if cur in ['bitcoin', 'ether']:
            return self.private_query('%s_withdrawal' % cur, params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, cur='bitcoin', **kwargs):
        if cur in ['bitcoin', 'ether']:
            return self.private_query('%s_deposit_address' % cur, params=kwargs)
        else:
            raise NotImplementedError("Invalid Currency! Must be %s|%s" %
                                      ('bitcoin', 'ether'))


    """
    Exchange Specific Methods
    """
