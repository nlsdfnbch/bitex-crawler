"""
https://api.vaultoro.com/#api-Basic_API
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import VaultoroREST
from bitex.utils import return_api_response
from bitex.formatters.vaultoro import VaultoroFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class Vaultoro(VaultoroREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Vaultoro, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

    def public_query(self, endpoint, method_verb=None, **kwargs):
        if not method_verb:
            method_verb = 'GET'
        return self.query(method_verb, endpoint, **kwargs)

    def private_query(self, endpoint, method_verb=None, **kwargs):
        if not method_verb:
            method_verb = 'GET'
        return self.query(method_verb, endpoint, authenticate=True,
                          **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        return self.public_query('orderbook')

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        return self.public_query('markets', params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, count=250, **kwargs):
        q = {'count': count}
        q.update(kwargs)
        return self.public_query('latesttrades', params=q)

    def _place_order(self, pair, size, price, side, order_type, **kwargs):
        args = side, pair, order_type
        q = {'gld': size, 'price': price}
        return self.private_query('1/%s/%s/%s' % args, params=kwargs,
                                  method_verb='POST')

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, order_type=None, **kwargs):
        if not order_type:
            order_type = 'limit'
        return self._place_order(pair, size, price, 'buy', order_type,
                                 **kwargs)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, order_type=None, **kwargs):
        if not order_type:
            order_type = 'limit'
        return self._place_order(pair, size, price, 'sell', order_type,
                                 **kwargs)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        return self.private_query('1/cancel/%s' % order_id, method_verb='POST',
                                  params=kwargs)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        return self.private_query('1/orders', params=kwargs)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('1/balance', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, *args, **kwargs):
        q = {'btc': size}
        q.update(kwargs)
        return self.private_query('1/withdraw', method_verb='POST', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError