"""
https://bittrex.com/Home/Api
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import BittrexREST
from bitex.utils import return_api_response
from bitex.formatters.bittrex import BtrxFormatter as fmt
# Init Logging Facilities
log = logging.getLogger(__name__)


class Bittrex(BittrexREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Bittrex, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', 'public/' + endpoint, **kwargs)

    def private_query(self, endpoint, **kwargs):
        return self.query('GET', endpoint, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        q = {'market': pair}
        q.update(kwargs)
        return self.public_query('getmarketsummary', params=q)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, side='both', **kwargs):
        q = {'market': pair, 'type': side}
        q.update(kwargs)
        return self.public_query('getorderbook', params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = {'market': pair}
        q.update(kwargs)
        return self.public_query('getmarkethistory', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, vol, market=False, **kwargs):
        q = {'market': pair, 'rate': price, 'quantity': vol}
        q.update(kwargs)
        if market:
            # send market order
            return self.private_query('market/buymarket', params=q)
        else:
            # send limit order
            return self.private_query('market/buylimit', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, price, vol, market=False, **kwargs):
        q = {'market': pair, 'rate': price, 'quantity': vol}
        q.update(kwargs)
        if market:
            # send market order
            return self.private_query('market/sellmarket', params=q)
        else:
            # send limit order
            return self.private_query('market/selllimit', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, txid):
        q = {'uuid': txid}
        return self.private_query('market/cancel', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        q = {'uuid': order_id}
        q.update(kwargs)
        return self.private_query('account/getorder', params=q)

    @return_api_response(fmt.balance)
    def balance(self):
        return self.private_query('account/getbalances')

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'quantity': size, 'address': tar_addr}
        q.update(kwargs)
        return self.private_query('account/withdraw', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        return self.private_query('account/getdepositaddress', params=kwargs)

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def pairs(self):
        return self.public_query('getmarkets')

    @return_api_response(None)
    def currencies(self):
        return self.public_query('getcurrencies')

    @return_api_response(None)
    def statistics(self, pair=None):
        if pair:
            return self.public_query('getmarketsummary', params={'market': pair})
        else:
            return self.public_query('getmarketsummaries')
