"""
https://www.cryptopia.co.nz/Forum/Category/45
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import CryptopiaREST
from bitex.utils import return_api_response
from bitex.formatters.cryptopia import CrptFormatter as fmt
# Init Logging Facilities
log = logging.getLogger(__name__)


class Cryptopia(CryptopiaREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Cryptopia, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)
        print(self.uri)

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, **kwargs)

    def private_query(self, endpoint, **kwargs):
        return self.query('POST', endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, *args, **kwargs):
        endpoint = 'GetMarket/%s' % pair
        for k in args:
            endpoint += '/' + k
        return self.public_query(endpoint, params=kwargs)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, *args, **kwargs):
        endpoint = 'GetMarketOrders/%s' % pair
        for k in args:
            endpoint += '/' + k
        return self.public_query(endpoint, params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, *args, **kwargs):
        endpoint = 'GetMarkets/%s' % pair
        for k in args:
            endpoint += '/' + k
        return self.public_query(endpoint, params=kwargs)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'Market': pair, 'Type': 'Buy', 'Rate': price, 'Amount': size}
        q.update(kwargs)
        return self.private_query('SubmitTrade', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'Market': pair, 'Type': 'Sell', 'Rate': price, 'Amount': size}
        q.update(kwargs)
        return self.private_query('SubmitTrade', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        q = {'OrderId': order_id}
        q.update(kwargs)
        return self.private_query('CancelTrade', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        raise NotImplementedError()

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('GetBalance', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'Amount': size, 'Address': tar_addr}
        q.update(kwargs)
        return self.private_query('SubmitWithdraw', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        return self.private_query('GetDepositAddress', params=kwargs)

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def currencies(self):
        return self.public_query('GetCurrencies')

    @return_api_response(None)
    def pairs(self):
        return self.public_query('GetTradePairs')

    @return_api_response(None)
    def markets(self, **kwargs):
        endpoint = 'GetMarkets'
        for k in kwargs:
            endpoint += '/' + kwargs[k]
        return self.public_query(endpoint, params=kwargs)
