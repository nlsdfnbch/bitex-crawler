"""
http://docs.bitfinex.com/
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import BitfinexREST
from bitex.api.WSS.bitfinex import BitfinexWSS
from bitex.utils import return_api_response
from bitex.formatters.bitfinex import BtfxFormatter as fmt
# Init Logging Facilities
log = logging.getLogger(__name__)


class Bitfinex(BitfinexREST):
    def __init__(self, key='', secret='', key_file='', websocket=False):
        super(Bitfinex, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)
        if websocket:
            self.wss = BitfinexWSS()
            self.wss.start()
        else:
            self.wss = None

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, **kwargs):
        return self.query('POST', endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """
    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        return self.public_query('book/%s' % pair, params=kwargs)

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        return self.public_query('pubticker/%s' % pair, params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        return self.public_query('trades/%s' % pair, params=kwargs)

    def _place_order(self, pair, size, price, side, replace, **kwargs):
        q = {'symbol': pair, 'amount': size, 'price': price, 'side': side,
             'type': 'exchange limit'}
        q.update(kwargs)
        if replace:
            return self.private_query('order/cancel/replace', params=q)
        else:
            return self.private_query('order/new', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, replace=False, **kwargs):
        return self._place_order(pair, size, price, 'buy', replace=replace,
                                 **kwargs)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, replace=False, **kwargs):
        return self._place_order(pair, str(size), str(price), 'sell',
                                 replace=replace, **kwargs)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, all=False, **kwargs):

        q = {'order_id': int(order_id)}
        q.update(kwargs)
        if not all:
            return self.private_query('order/cancel', params=q)
        else:
            endpoint = 'order/cancel/all'
            return self.private_query(endpoint)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'order_id': order_id}
        q.update(kwargs)
        return self.private_query('order/status', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('balances', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'withdraw_type': kwargs.pop('withdraw_type'),
             'walletselected': kwargs.pop('walletselected'),
             'amount': size, 'address': tar_addr}
        q.update(kwargs)
        return self.private_query('withdraw', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        q = {}
        q.update(kwargs)
        return self.private_query('deposit/new', params=kwargs)

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def statistics(self, pair):
        return self.public_query('stats/%s' % pair)

    @return_api_response(None)
    def funding_book(self, currency, **kwargs):
        return self.public_query('lendbook/%s' % currency, params=kwargs)

    @return_api_response(None)
    def lends(self, currency, **kwargs):
        return self.public_query('lends/%s' % currency, params=kwargs)

    @return_api_response(None)
    def pairs(self, details=False):
        if details:
            return self.public_query('symbols_details')
        else:
            return self.public_query('symbols')

    @return_api_response(None)
    def fees(self):
        return self.private_query('account_infos')

    @return_api_response(None)
    def orders(self):
        return self.private_query('orders')

    @return_api_response(None)
    def balance_history(self, currency, **kwargs):
        q = {'currency': currency}
        q.update(kwargs)
        return self.private_query('history/movements', params=q)

    @return_api_response(None)
    def trade_history(self, pair, since, **kwargs):
        q = {'symbol': pair, 'timestamp': since}
        q.update(kwargs)
        return self.private_query('mytrades', params=q)

    @return_api_response(None)
    def positions(self):
        return self.private_query('positions')

    @return_api_response(None)
    def credits(self):
        return self.private_query('credits')
    
    @return_api_response(None)
    def new_offer(self, currency, amount, rate, period, direction, **kwargs):
        q = {'currency': currency, 'amount': amount, 'rate': rate, 'period': period, 'period': direction }
        q.update(kwargs)
        return self.private_query('offer/new', params=q)
    
    @return_api_response(None)
    def cancel_offer(self, id, **kwargs):
        q = {'id': id}
        q.update(kwargs)
        return self.private_query('offer/cancel', params=q)
