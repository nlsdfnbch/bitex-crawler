"""Bitfinex Interface class."""
# Import Built-Ins
import logging
from bitex.api.REST.bitfinex import BitfinexREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_version_compatibility, check_and_format_pair, format_with
from bitex.formatters import BitfinexFormattedResponse
from bitex.exceptions import PairFetchError

# Init Logging Facilities
log = logging.getLogger(__name__)


class Bitfinex(RESTInterface):
    """Bitfinex Interface class.

    Includes standardized methods, as well as all other Endpoints
    available on their REST API.
    """

    # pylint: disable=arguments-differ

    # State version specific methods
    v2_only_methods = ['candles', 'market_average_price', 'wallets', 'orders',
                       'order_trades', 'positions', 'offers', 'funding_info',
                       'performance', 'alert_set', 'alert_list',
                       'alert_delete', 'calc_available_balance']
    v1_only_methods = ['new_order', 'tickers', 'symbols', 'symbols_details',
                       'account_info', 'account_fees', 'summary', 'deposit',
                       'key_info', 'balances', 'transfer', 'withdrawal',
                       'cancel_order', 'order_status', 'open_orders',
                       'cancel_all_orders', 'cancel_multiple_orders',
                       'replace_order', 'active_orders', 'active_positions',
                       'active_credits', 'balance_history', 'past_trades',
                       'deposit_withdrawal_history', 'new_offer', 'cancel_offer',
                       'offer_status', 'unused_taken_funds', 'taken_funds',
                       'total_taken_funds', 'close_funding', 'basket_manage',
                       'lends', 'funding_book']

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Bitfinex, self).__init__('Bitfinex', BitfinexREST(**api_kwargs))

    def request(self, endpoint, authenticate=False, **req_kwargs):
        """Generate a request to the API."""
        if not authenticate:
            return super(Bitfinex, self).request('GET', endpoint, authenticate=authenticate,
                                                 **req_kwargs)
        return super(Bitfinex, self).request('POST', endpoint, authenticate=authenticate,
                                             **req_kwargs)

    def _get_supported_pairs(self):
        """Return supported pairs."""
        if self.REST.version == 'v1':  # default if v1
            r = self.symbols()
        else:
            r = super(Bitfinex, self).request('GET', 'https://api.bitfinex.com/v1/symbols',
                                              endpointwithversion=True)
        if not r.ok:
            raise PairFetchError(r.ok,r.status_code,r.reason)
        pairs=r.json()
        if not isinstance(pairs, list):
            raise PairFetchError(pairs)

        pairs = [p.upper() for p in pairs]
        return pairs

    def _get_supported_pairs_formatted(self):
        """Return a list of supported pairs."""
        pairs = self._supported_pairs
        pairs_formatted = []
        for pair in pairs:
            base = pair[:-3]
            if base == 'DSH':
                base = 'DASH'
            pairs_formatted.append((base + '_' + pair[-3:]).upper())
        return pairs_formatted

    ###############
    # Basic Methods
    ###############

    @check_and_format_pair
    @format_with(BitfinexFormattedResponse)
    def order_book(self, pair, **endpoint_kwargs):
        """Return the order book for a given pair."""
        self.is_supported(pair)
        if self.REST.version == 'v1':
            return self.request('book/%s' % pair, params=endpoint_kwargs)
        prec = endpoint_kwargs.pop('Precision', 'P0')
        return self.request('book/t%s/%s' % (pair, prec), params=endpoint_kwargs)

    @format_with(BitfinexFormattedResponse)
    @check_and_format_pair
    def ticker(self, pair, **endpoint_kwargs):
        """Return the ticker for a given pair."""
        self.is_supported(pair)
        if self.REST.version == 'v1':
            return self.request('pubticker/%s' % pair)
        return self.request('ticker/t%s' % pair, params=endpoint_kwargs)

    @check_and_format_pair
    @format_with(BitfinexFormattedResponse)
    def trades(self, pair, **endpoint_kwargs):
        """Return trades for a given pair."""
        self.is_supported(pair)
        if self.REST.version == 'v1':
            return self.request('trades/%s' % pair, params=endpoint_kwargs)
        return self.request('trades/t%s/hist' % pair, params=endpoint_kwargs)

    @check_and_format_pair
    @format_with(BitfinexFormattedResponse)
    def ask(self, pair, price, size, *args, market=False, **kwargs):
        """Place an ask order with the given parameters."""
        return self._place_order(pair, price, size, 'sell', market=market, **kwargs)

    @check_and_format_pair
    @format_with(BitfinexFormattedResponse)
    def bid(self, pair, price, size, *args, market=False, **kwargs):
        """Place a bid order with the given parameters."""
        return self._place_order(pair, price, size, 'buy', market=market, **kwargs)

    def _place_order(self, pair, price, size, side, market=None, **kwargs):
        """Place an order with the given parameters."""
        if market:
            payload = {'symbol': pair, 'price': str(price), 'amount': str(size), 'side': side,
                       'type': 'exchange market'}
        else:
            payload = {'symbol': pair, 'price': str(price), 'amount': str(size), 'side': side,
                       'type': 'exchange limit'}
        payload.update(kwargs)
        return self.new_order(pair, **payload)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @format_with(BitfinexFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """Return the order status for the given id."""
        return self.request('order/status', authenticate=True, params={'order_id': int(order_id)})

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @format_with(BitfinexFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return a list of open orders."""
        return self.active_orders(*args, **kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @format_with(BitfinexFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """Cancel orders with the given ids."""
        results = []
        payload = kwargs
        for oid in order_ids:
            payload.update({'order_id': int(oid)})
            r = self.request('order/cancel', authenticate=True,
                             params=payload)
            results.append(r)
        return results if len(results) > 1 else results[0]

    @format_with(BitfinexFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return the account's wallet."""
        return self.balances()

    ###########################
    # Exchange Specific Methods
    ###########################

    #########################
    # Version Neutral Methods
    #########################

    @check_and_format_pair
    def stats(self, pair, **endpoint_kwargs):
        """Return statistics about the account."""
        self.is_supported(pair)
        if self.REST.version == 'v1':
            return self.request('stats/%s' % pair)
        key = endpoint_kwargs.pop('key')
        size = endpoint_kwargs.pop('size')
        side = endpoint_kwargs.pop('side')
        section = endpoint_kwargs.pop('section')
        path = key, size, pair, side, section
        return self.request('stats1/%s:%s:%s:%s/%s' % path, params=endpoint_kwargs)

    def margin_info(self, **endpoint_kwargs):
        """Return margin information."""
        if self.REST.version == 'v1':
            return self.request('margin_info', authenticate=True)
        key = endpoint_kwargs.pop('key')
        return self.request('auth/r/margin/%s' % key, authenticate=True, params=endpoint_kwargs)

    def offers(self, **endpoint_kwargs):
        """Return all offers placed via the account."""
        if self.REST.version == 'v1':
            return self.request('offers', authenticate=True, params=endpoint_kwargs)
        return self.request('auth/r/offers', authenticate=True, params=endpoint_kwargs)

    ########################
    # Version 1 Only Methods
    ########################

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def tickers(self):
        """Return all tickers."""
        return self.request('tickers')

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def symbols(self, verbose=False):
        """Return a list of all available symbols."""
        if verbose:
            return self.request('symbols_details')
        return self.request('symbols')

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def symbols_details(self):
        """Return a list of all available symbols and their details."""
        return self.request('symbols_details')

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def lends(self, currency, **endpoint_kwargs):
        """Return all open lend positions."""
        return self.request('lends/%s' % currency, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def funding_book(self, currency, **endpoint_kwargs):
        """Return the funding book for the given currency."""
        return self.request('lendbook/%s' % currency, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def account_info(self):
        """Return account information."""
        return self.request('account_infos', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def account_fees(self):
        """Return current fees for the account."""
        return self.request('account_fees', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def summary(self):
        """Return account summary."""
        return self.request('summary', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def deposit(self, **endpoint_kwargs):
        """Deposit currency."""
        return self.request('deposit', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def key_info(self):
        """Return key information."""
        return self.request('key_info', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def funding_info(self, pair, **endpoint_kwargs):
        """Return funcing information for the account."""
        return self.request('auth/r/funding/%s' % pair, authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def balances(self):
        """Return the account balances."""
        return self.request('balances', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def transfer(self, **endpoint_kwargs):
        """Transfer currency."""
        return self.request('transfer', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def withdrawal(self, **endpoint_kwargs):
        """Withdraw currency."""
        return self.request('withdraw', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def new_order(self, pair, **endpoint_kwargs):
        """Place a new order."""
        self.is_supported(pair)
        payload = {'symbol': pair}
        payload.update(endpoint_kwargs)
        return self.request('order/new', authenticate=True, params=payload)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def multiple_new_orders(self, *orders):
        """Place multiple new orders."""
        raise NotImplementedError

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def cancel_multiple_orders(self, *order_ids):
        """Cancel multiple orders."""
        return self.request('order/cancel/multi', authenticate=True,
                            params={'order_ids': order_ids})

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def cancel_all_orders(self):
        """Cancel all orders."""
        return self.request('order/cancel/all', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def replace_order(self, **endpoint_kwargs):
        """Substitute an order."""
        return self.request('order/cancel/replace', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def active_orders(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Return active orders."""
        return self.request('orders', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def active_positions(self):
        """Return active positions."""
        return self.request('positions', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def claim_position(self, **endpoint_kwargs):
        """Return currently claimed positions."""
        return self.request('position/claim', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def balance_history(self, **endpoint_kwargs):
        """Return balance history of the account."""
        return self.request('history', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def deposit_withdrawal_history(self, **endpoint_kwargs):
        """Return the deposit/withdrawal history of the account."""
        return self.request('history/movement', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def past_trades(self, pair, **endpoint_kwargs):
        """Return past trades of the account."""
        self.is_supported(pair)
        payload = {'symbol': pair}
        payload.update(endpoint_kwargs)
        return self.request('mytrades', authenticate=True, params=payload)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def new_offer(self, **endpoint_kwargs):
        """Place a new offer."""
        return self.request('offer/new', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def cancel_offer(self, **endpoint_kwargs):
        """Cancel an existing offer."""
        return self.request('offer/cancel', authenticate=False, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def offer_status(self, **endpoint_kwargs):
        """Return offer status."""
        return self.request('offer/status', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def active_credits(self, **endpoint_kwargs):
        """Return active given credits."""
        return self.request('credits', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def taken_funds(self, **endpoint_kwargs):
        """Return taken funds."""
        return self.request('taken_funds', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def unused_taken_funds(self, **endpoint_kwargs):
        """Return available funds."""
        return self.request('unused_taken_funds', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def total_taken_funds(self, **endpoint_kwargs):
        """Return total taken funds."""
        return self.request('total_taken_funds', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def close_funding(self, **endpoint_kwargs):
        """Close funding."""
        return self.request('funding/close', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def basket_manage(self, **endpoint_kwargs):
        """See bitfinex docs."""
        return self.request('basket_manage', authenticate=True, params=endpoint_kwargs)

    ########################
    # Version 2 Only Methods
    ########################
    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def candles(self, pair, **endpoint_kwargs):
        """Return candle data."""
        time_frame = endpoint_kwargs.pop('time_frame')
        section = endpoint_kwargs.pop('section')
        return self.request('candles/trade:%s:t%s/%s' % (time_frame, pair.upper(), section),
                            params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def market_average_price(self, pair, **endpoint_kwargs):
        """Return average market price for pair."""
        self.is_supported(pair)
        return self.request('calc/trade/avg', data=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def wallets(self):
        """Return the account's wallets."""
        return self.request('auth/r/wallets', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def orders(self):
        """Return all open orders."""
        return self.request('auth/r/orders', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def order_trades(self, pair, order_id, **endpoint_kwargs):
        """Return trades of the account."""
        return self.request('auth/r/order/%s:%s/trades' % (pair, order_id),
                            authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def positions(self):
        """Return open positions."""
        return self.request('auth/r/positions', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def performance(self):
        """Return account performance."""
        return self.request('auth/r/stats/perf:1D/hist', authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    def alert_list(self, **endpoint_kwargs):
        """Return a list of active alerts."""
        price = endpoint_kwargs.pop('type')
        return self.request('auth/r/alerts?type=%s' % price, authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def alert_set(self, pair, **endpoint_kwargs):
        """Set a new alert for the given pair."""
        self.is_supported(pair)
        endpoint_kwargs['symbol'] = pair
        return self.request('auth/w/alert/set', authenticate=True, params=endpoint_kwargs)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def alert_delete(self, pair, **endpoint_kwargs):
        """Delete an alert for the given pair."""
        self.is_supported(pair)
        price = endpoint_kwargs.pop('price')
        return self.request('auth/w/alert/price:%s:%s/del' % (pair, price), authenticate=True)

    @check_version_compatibility(v1=v1_only_methods, v2=v2_only_methods)
    @check_and_format_pair
    def calc_available_balance(self, pair, **endpoint_kwargs):
        """Calculate the currently available balance."""
        self.is_supported(pair)
        endpoint_kwargs['symbol'] = pair
        return self.request('auth/calc/order/avail', authenticate=True, params=endpoint_kwargs)
