"""
https://bter.com/api
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import BterREST
from bitex.utils import return_api_response
from bitex.formatters.bter import BterFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class Bter(BterREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Bter, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, method_verb=None, **kwargs):
        if not method_verb:
            method_verb = 'POST'
        endpoint = 'private/' + endpoint
        return self.query(method_verb, endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        return self.public_query('depth/%s' % pair, params=kwargs)

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        if pair == 'all':
            return self.public_query('tickers', params=kwargs)
        else:
            return self.public_query('ticker/%s' % pair, params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        return self.public_query('trade/%s' % pair, params=kwargs)

    def _place_order(self, pair, size, price, side, **kwargs):
        q = {'pair': pair, 'type': side, 'price': price, 'amount': size}
        q.update(kwargs)
        return self.private_query('placeorder', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        return self._place_order(pair, size, price, 'BUY', **kwargs)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        return self._place_order(pair, size, price, 'SELL', **kwargs)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        q = {'order_id': order_id}
        q.update(kwargs)
        return self.private_query('cancelorder', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'order_id': order_id}
        q.update(kwargs)
        return self.private_query('getorder', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('getfunds', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        raise NotImplementedError

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError