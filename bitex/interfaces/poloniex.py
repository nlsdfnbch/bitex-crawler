"""
https://poloniex.com/support/api/
"""

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST.rest import PoloniexREST
from bitex.api.WSS.poloniex import PoloniexWSS
from bitex.utils import return_api_response
from bitex.formatters.poloniex import PlnxFormatter as fmt
# Init Logging Facilities
log = logging.getLogger(__name__)


class Poloniex(PoloniexREST):
    def __init__(self, key='', secret='', key_file='', websocket=False):
        super(Poloniex, self).__init__(key, secret)
        if key_file:
            self.load_key(key_file)
        if websocket:
            self.wss = PoloniexWSS()
            self.wss.start()
        else:
            self.wss = None

    def public_query(self, endpoint, **kwargs):
        return self.query('GET', 'public?command=' + endpoint, **kwargs)

    def private_query(self, endpoint, **kwargs):
        return self.query('POST', endpoint,
                          authenticate=True, **kwargs)

    """
    BitEx Standardized Methods
    """

    @return_api_response(fmt.ticker)
    def ticker(self, pair, **kwargs):
        return self.public_query('returnTicker', params=kwargs)

    @return_api_response(fmt.order_book)
    def order_book(self, pair, **kwargs):
        kwargs['currencyPair'] = pair
        return self.public_query('returnOrderBook', params=kwargs)

    @return_api_response(fmt.trades)
    def trades(self, pair, **kwargs):
        kwargs['currencyPair'] = pair
        return self.public_query('returnTradeHistory', params=kwargs)

    @return_api_response(fmt.order)
    def bid(self, pair, rate, size, **kwargs):
        q = {'command': 'buy', 'currencyPair': pair, 'amount': size,
             'rate': rate}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(fmt.order)
    def ask(self, pair, rate, size, **kwargs):
        q = {'command': 'sell', 'currencyPair': pair, 'amount': size,
             'rate':    rate}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(fmt.cancel)
    def cancel_order(self, txid, **kwargs):
        q = {'orderNumber': txid, 'command': 'cancelOrder'}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(fmt.order_status)
    def order(self, order_id, **kwargs):
        raise NotImplementedError()

    @return_api_response(fmt.balance)
    def balance(self, detailed=False, **kwargs):
        q = {}
        if detailed:
            q['command'] = 'returnCompleteBalances'
        else:
            q['command'] = 'returnBalances'
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(fmt.withdraw)
    def withdraw(self, size, tar_addr, **kwargs):
        q = {'currency': kwargs.pop('currency'), 'amount': size, 'address': tar_addr}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(fmt.deposit)
    def deposit_address(self, currency, **kwargs):
        q = {'command': 'returnDepositAddresses'}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)


    """
    Exchange Specific Methods
    """

    @return_api_response(None)
    def currencies(self):
        return self.public_query('returnCurrencies')

    @return_api_response(None)
    def hloc(self, pair, **kwargs):
        kwargs['currencyPair'] = pair
        return self.public_query('returnChartData')


    @return_api_response(None)
    def balance_history(self, **kwargs):
        q = {'command': 'returnDepositsWithdrawals'}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(None)
    def orders(self, pair='all', **kwargs):
        q = {'command': 'returnOpenOrders', 'currencyPair': pair}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(None)
    def trade_history(self, pair='all', **kwargs):
        q = {'currencyPair': pair, 'command': 'returnTradeHistory'}
        q.update(kwargs)
        return self.private_query('tradingApi', params=q)

    @return_api_response(None)
    def update_order(self, txid, rate, **kwargs):
        q = {'command': 'moveOrder', 'rate': rate, 'orderNumber': txid}
        q.update(kwargs)
        return self.query('tradingApi', params=q)

    @return_api_response(None)
    def fees(self):
        return self.private_query('tradingApi',
                                  params={'command': 'returnFeeInfo'})
