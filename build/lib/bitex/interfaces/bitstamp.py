"""
https://www.bitstamp.net/api/
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import BitstampREST
from bitex.api.WSS.bitstamp import BitstampWSS
from bitex.utils import return_api_response
from bitex.formatters.bitstamp import BtstFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class Bitstamp(BitstampREST):
    def __init__(self, key='', secret='', key_file='', websocket=False):
        super(Bitstamp, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

        if websocket:
            self.wss = BitstampWSS()
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

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        return self.public_query('v2/ticker/%s/' % pair, params=kwargs)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        return self.public_query('v2/order_book/%s' % pair, params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        return self.public_query('v2/transactions/%s' % pair, params=kwargs)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'amount': size, 'price': price}
        q.update(kwargs)
        return self.private_query('v2/buy/%s/' % pair, params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'amount': size, 'price': price}
        q.update(kwargs)
        return self.private_query('v2/sell/%s/' % pair, params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, all=False, **kwargs):
        return self.private_query('cancel_order/', params={'id': order_id})

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'id': order_id}
        q.update(kwargs)
        return self.private_query('order_status/', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('v2/balance/')

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'amount': size, 'address': tar_addr}
        q.update(kwargs)
        return self.private_query('bitcoin_withdrawal/', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        return self.private_query('bitcoin_deposit_address/')

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def hourly_ticker(self, pair):
        return self.public_query('v2/ticker_hour/%s' % pair)

    @return_api_response(None)
    def eurusd_rate(self):
        return self.public_query('eur_usd')

    def pairs(self):
        return ['btcusd', 'btceur', 'eurusd']
