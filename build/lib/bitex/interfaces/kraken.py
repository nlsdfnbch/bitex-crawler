"""
https:/kraken.com/help/api
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import KrakenREST
from bitex.utils import return_api_response
from bitex.formatters.kraken import KrknFormatter as fmt
# Init Logging Facilities
log = logging.getLogger(__name__)


class Kraken(KrakenREST):
    def __init__(self, key='', secret='', key_file=''):
        super(Kraken, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)

    def make_params(self, *pairs, **kwargs):
        q = {'pair': ','.join(pairs)}
        q.update(kwargs)
        return q

    def public_query(self, endpoint, **kwargs):
        path = 'public/' + endpoint
        return self.query('GET', path, **kwargs)

    def private_query(self, endpoint, **kwargs):
        path = 'private/' + endpoint
        return self.query('POST', path, authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, *pairs, **kwargs):
        q = self.make_params(*pairs, **kwargs)
        return self.public_query('Ticker', params=q)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        q = self.make_params(pair, **kwargs)
        return self.public_query('Depth', params=q)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        q = self.make_params(pair, **kwargs)
        return self.public_query('Trades', params=q)

    def _add_order(self, pair, side, price, size, **kwargs):
        q = {'pair': pair, 'type': side, 'price': price,
             'ordertype': 'limit', 'volume': size,
             'trading_agreement': 'agree'}
        q.update(kwargs)
        return self.private_query('AddOrder', params=q)

    @return_api_response(fmt.order)
    def bid(self, pair, price, size, **kwargs):
        return self._add_order(pair, 'buy', price, size, **kwargs)

    @return_api_response(fmt.order)
    def ask(self, pair, price, size, **kwargs):
        return self._add_order(pair, 'sell', price, size, **kwargs)

    @return_api_response(fmt.cancel)
    def cancel_order(self, order_id, **kwargs):
        q = {'txid': order_id}
        q.update(kwargs)
        return self.private_query('CancelOrder', params=q)

    @return_api_response(fmt.order_status)
    def order(self, *txids, **kwargs):
        if len(txids) > 1:
            q = {'txid': txids}
        elif txids:
            txid, *_ = txids
            q = {'txid': txid}
        else:
            q = {}
        q.update(kwargs)
        return self.private_query('QueryOrders', params=q)

    @return_api_response(fmt.balance)
    def balance(self, **kwargs):
        return self.private_query('Balance')

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'amount': size, 'key': tar_addr}
        q.update(kwargs)
        return self.private_query('Withdraw', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, **kwargs):
        return self.private_query('DepositAddresses', params=kwargs)

    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def time(self):
        return self.public_query('Time')

    @return_api_response(None)
    def assets(self, **kwargs):
        return self.public_query('Assets', params=kwargs)

    @return_api_response(None)
    def pairs(self, **kwargs):
        return self.public_query('AssetPairs', params=kwargs)

    @return_api_response(None)
    def ohlc(self, pair, **kwargs):
        q = self.make_params(pair, **kwargs)
        return self.public_query('OHLC', params=q)

    @return_api_response(None)
    def spread(self, pair, **kwargs):
        q = self.make_params(pair, **kwargs)
        return self.public_query('Spread', params=q)

    @return_api_response(None)
    def orders(self, **kwargs):
        q = kwargs
        return self.private_query('OpenOrders', params=q)

    @return_api_response(None)
    def closed_orders(self, **kwargs):
        q = kwargs
        return self.private_query('ClosedOrders', params=q)

    @return_api_response(None)
    def trade_history(self, **kwargs):
        q = kwargs
        return self.private_query('TradesHistory', params=q)

    @return_api_response(None)
    def fees(self, pair=None):
        q = {'fee-info': True}

        if pair:
            q['pair'] = pair

        return self.private_query('TradeVolume', params=q)

    def deposit_methods(self, **kwargs):
        return self.private_query('DepositMethods', params=kwargs)

    def withdraw_info(self, size, tar_addr, **kwargs):
        q = {'amount': size, 'key': tar_addr}
        q.update(kwargs)
        return self.private_query('WithdrawInfo', params=q)
