"""
https://c-cex.com/?id=api
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import CCEXRest
from bitex.utils import return_api_response
from bitex.formatters.ccex import CcexFormatter as fmt

# Init Logging Facilities
log = logging.getLogger(__name__)


class CCEX(CCEXRest):
    def __init__(self, key='', secret='', key_file=''):
        super(CCEX, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)
        print(self.uri)

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', 'api_pub.html?a=' + endpoint, **kwargs)

    def private_query(self, endpoint, **kwargs):
        return self.query('POST', 'api.html?a=' + endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        return self.public_query('%s.json' % pair, params=kwargs)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, type='both', **kwargs):
        q = {'market': pair, 'type': type}
        q.update(kwargs)
        return self.public_query('getorderbook', params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = {'market': pair}
        q.update(kwargs)
        return self.public_query('getmarkethistory',
                                 params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        q = {'market': pair, 'rate': price, 'quantity': size}
        q.update(kwargs)
        return self.private_query('buylimit', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        q = {'market': pair, 'rate': price, 'quantity': size}
        q.update(kwargs)
        return self.private_query('buylimit', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        q = {'uuid': order_id}
        q.update(kwargs)
        return self.private_query('cancel', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'uuid': order_id}
        q.update(kwargs)
        return self.private_query('getorder', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('getbalance', params=kwargs)

    @return_api_response(fmt.withdraw)
    def withdraw(self, _type, source_wallet, size, tar_addr, **kwargs):
        raise NotImplementedError()

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        raise NotImplementedError()

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def pairs(self, names_only=True):
        if names_only:
            return self.public_query('api_pub.html?a=getmarkets')
        else:
            return self.public_query('pairs.json')

    @return_api_response(None)
    def prices(self):
        return self.public_query('prices.json')

    @return_api_response(None)
    def coin_names(self):
        return self.public_query('coinnames.json')

    @return_api_response(None)
    def volume(self, pair):
        return self.public_query('volume_%s.json' % pair)

    @return_api_response(None)
    def statistics(self, all=True):
        if all:
            return self.public_query('api_pub.html?a=getmarketsummaries')

    @return_api_response(None)
    def balance_distribution(self, currency):
        return self.public_query('api_pub.html?a=getbalancedistribution',
                                 params={'currencyname': currency})
