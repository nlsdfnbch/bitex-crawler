"""
Includes the base class for crypto currency pairs and the PairFormatter class.

It also provides convencience wrappers for commonly used Pairs: these can be
imported to avoid typos by the user, and can be directly passed to the APIs.

If the pair you want to query isn't present in here, creating such a pair is
simple enough - simply initialize the PairFormatter class with the currencies
you want::

    >>> my_pair = PairFormatter('BaseCurrency', 'QuoteCurrency')

The object ``my_pair`` now takes care of all formatting of any exchange,
supported by Bitex, you pass it to.
"""

# pylint: disable=too-many-public-methods,missing-docstring

# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


class PairFormatter:
    """Container Class which features formatting function for all supported exchanges.

    These Formatter functions apply any changes to make a given
    pair, pased as quote and base currency, compatible with an exchange.
    This does NOT include an availability check of the pair.
    It is therefore possible to format a given pair, even though it is not
    supported by the requested exchange.
    """

    def __init__(self, base, quote):
        """Initialize formatter instance."""
        self._base = base
        self._quote = quote
        self.formatters = {'Kraken': self.kraken_formatter,
                           'Bitstamp': self.bitstamp_formatter,
                           'Bitfinex': self.bitfinex_formatter,
                           'Bittrex': self.bittrex_formatter,
                           'CoinCheck': self.coincheck_formatter,
                           'GDAX': self.gdax_formatter,
                           'ITBit': self.itbit_formatter,
                           'OKCoin': self.okcoin_formatter,
                           'OKex': self.okex_formatter,
                           'C-CEX': self.ccex_formatter,
                           'Cryptopia': self.cryptopia_formatter,
                           'Gemini': self.gemini_formatter,
                           'The Rock Trading Ltd.': self.rocktrading_formatter,
                           'Poloniex': self.poloniex_formatter,
                           'Quoine': self.quoine_formatter,
                           'QuadrigaCX': self.quadriga_formatter,
                           'HitBTC': self.hitbtc_formatter,
                           'Vaultoro': self.vaultoro_formatter,
                           'Bter': self.bter_formatter,
                           'Yunbi': self.yunbi_formatter,
                           "Binance": self.binance_formatter,
                           'Bithumb': self.bithumb_formatter,
                           'Coinone': self.coinone_formatter,
                           'CEXio': self.cexio_formatter,
                           'Exmo': self.exmo_formatter,
                           'Coinnest': self.coinnest_formatter,
                           'Gateio': self.gateio_formatter,}

    def __str__(self, *args, **kwargs):
        """Return the stored base and quote currency in proper pair format."""
        return self._base + self._quote

    def __call__(self):
        """Return currency pair when called."""
        return self.__str__()

    def format_for(self, exchange_name):
        """Format the pair for the given exchange."""
        return self.formatters[exchange_name](self._base, self._quote)

    @staticmethod
    def kraken_formatter(base, quote):
        """Format the currencies for Kraken.

        Generally speaking, Kraken prefixes digital currencies with a capital 'X', and fiat
        Currencies with a capital 'Z'. There exceptions to this rule, unfortunately,
        which should be handled as well.
        """
        base = 'XBT' if base == 'BTC' else base
        quote = 'XBT' if quote == 'BTC' else quote
        format_exceptions = ['BCHEUR', 'BCHUSD', 'BCHXBT', 'DASHEUR', 'DASHUSD', 'DASHXBT',
                             'EOSETH', 'EOSXBT', 'GNOETH', 'GNOXBT']

        def add_prefix(cur):
            """Add the correct prefix to the currency."""
            if 'BCH' in (base, quote):
                return cur
            elif cur in ('USD', 'EUR', 'GBP', 'JPY', 'CAD'):
                return 'Z' + cur
            return 'X' + cur

        if (base + quote).upper() in format_exceptions:
            return (base + quote).upper()
        elif (base + quote).upper() in ['USDTUSD', ]:
            return base + add_prefix(quote)

        return add_prefix(base) + add_prefix(quote)

    @staticmethod
    def bitstamp_formatter(base, quote):
        """Format currencies for Bitstamp."""
        return base.lower() + quote.lower()

    @staticmethod
    def bithumb_formatter(base, quote):
        """Format currencies for BitHumb."""
        return base.upper()

    @staticmethod
    def coinone_formatter(base, quote):
        """Format currencies for CoinOne."""
        return base.lower()

    @staticmethod
    def coinnest_formatter(base, quote):
        """Format currencies for CoinNest."""
        return base.lower()

    @staticmethod
    def cexio_formatter(base, quote):
        """Format currencies for CEXIO."""
        return base.upper() + quote.upper()

    @staticmethod
    def bitfinex_formatter(base, quote):
        """Format currencies for bitfinex.

        Edgecase: ``DASH``
            This symbol is shortened to ``DSH``.
        """
        base = 'DSH' if base == 'DASH' else base
        quote = 'DSH' if quote == 'DASH' else quote
        return base.upper() + quote.upper()

    @staticmethod
    def bittrex_formatter(base, quote):
        """Format currencies for Bittrex."""
        # quote = 'USDT' if quote == 'USD' else quote
        return quote + '-' + base

    @staticmethod
    def binance_formatter(base, quote):
        """Format currencies for Binance."""
        # quote = 'USDT' if quote == 'USD' else quote
        return base + quote

    @staticmethod
    def coincheck_formatter(base, quote):
        """Format currencies for CoinCheck."""
        return base.lower() + '_' + quote.lower()

    @staticmethod
    def exmo_formatter(base, quote):
        """Format currencies for Exmo."""
        return base.upper() + '_' + quote.upper()

    @staticmethod
    def gateio_formatter(base, quote):
        """Format currencies for Gate.io."""
        # quote = 'USDT' if quote == 'USD' else quote
        return base.lower() + '_' + quote.lower()

    @staticmethod
    def gdax_formatter(base, quote):
        """Format currencies for GDAX."""
        return base + '-' + quote

    @staticmethod
    def itbit_formatter(base, quote):
        """Format currencies for ItBit.

        Edge case: ``BTC``
            BTC is denoted as ``XBT``.
        """
        base = 'XBT' if base == 'BTC' else base
        quote = 'XBT' if base == 'BTC' else quote
        return base + quote

    @staticmethod
    def okcoin_formatter(base, quote):
        """Format currencies for OKCoin."""
        return base.lower() + '_' + quote.lower()

    @staticmethod
    def okex_formatter(base, quote):
        """Format currencies for OKCoin."""
        # quote = 'USDT' if quote == 'USD' else quote
        return base.lower() + '_' + quote.lower()

    @staticmethod
    def ccex_formatter(base, quote):
        """Format currencies for C-CEX."""
        return base.lower() + '-' + quote.lower()

    @staticmethod
    def cryptopia_formatter(base, quote):
        """Format currencies for Cryptopia."""
        return base + '_' + quote

    @staticmethod
    def gemini_formatter(base, quote):
        """Format currencies for Gemini."""
        return base.lower() + quote.lower()

    @staticmethod
    def yunbi_formatter(base, quote):
        """Format currencies for Yunbi."""
        return base.lower() + quote.lower()

    @staticmethod
    def rocktrading_formatter(base, quote):
        """Format currencies for The Rock Trading LTD."""
        return base + quote

    @staticmethod
    def poloniex_formatter(base, quote):
        """Format currencies for Poloniex.

        Edge Case: ``BTC``, ``USDT`` and ``XMR`` in Quote.
            As theses symbols have their own markets (several currencies are quoted in them),
            they must be handled accordingly.
        """
        # quote = 'USDT' if quote == 'USD' else quote
        if ((quote == 'BTC') or (quote == 'USDT') or
                (quote == 'XMR' and not (base == 'BTC' or base == 'USDT'))):
            return quote + '_' + base
        return base + '_' + quote

    @staticmethod
    def quoine_formatter(base, quote):
        """Format currencies for Quoine."""
        return base + quote

    @staticmethod
    def quadriga_formatter(base, quote):
        """Format currencies for QuadrigaCX."""
        return base.lower() + '_' + quote.lower()

    @staticmethod
    def hitbtc_formatter(base, quote):
        """Format currencies for HitBTC."""
        return base + quote

    @staticmethod
    def vaultoro_formatter(base, quote):
        """Format currencies for Vaultoro."""
        return base + '-' + quote

    @staticmethod
    def bter_formatter(base, quote):
        """Format currencies for BTer."""
        return base.lower() + '_' + quote.lower()

    @staticmethod
    def poloniex_unformatter(pair):
        """Unformat the pair for poloniex exchange.

        Removes seperator, swapps base and quote.
        """
        (base, quote) = pair.split('_')
        return quote.upper() + base.upper()


class BTCKRWFormatter(PairFormatter):
    """BTC/KRW PairFormatter object."""

    def __init__(self):
        """init."""
        super(BTCKRWFormatter, self).__init__('BTC', 'KRW')


class BTCUSDFormatter(PairFormatter):
    """BTC/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(BTCUSDFormatter, self).__init__('BTC', 'USD')


class ETHUSDFormatter(PairFormatter):
    """ETH/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(ETHUSDFormatter, self).__init__('ETH', 'USD')


class XMRUSDFormatter(PairFormatter):
    """XMR/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(XMRUSDFormatter, self).__init__('XMR', 'USD')


class ETCUSDFormatter(PairFormatter):
    """ETC/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(ETCUSDFormatter, self).__init__('ETC', 'USD')


class ZECUSDFormatter(PairFormatter):
    """ZEC/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(ZECUSDFormatter, self).__init__('ZEC', 'USD')


class DASHUSDFormatter(PairFormatter):
    """DASH/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(DASHUSDFormatter, self).__init__('DASH', 'USD')


class BCHUSDFormatter(PairFormatter):
    """BCH/USD PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(BCHUSDFormatter, self).__init__('BCH', 'USD')


class ETHBTCFormatter(PairFormatter):
    """ETH/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(ETHBTCFormatter, self).__init__('ETH', 'BTC')


class LTCBTCFormatter(PairFormatter):
    """LTC/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(LTCBTCFormatter, self).__init__('LTC', 'BTC')


class XMRBTCFormatter(PairFormatter):
    """XMR/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(XMRBTCFormatter, self).__init__('XMR', 'BTC')


class ETCBTCFormatter(PairFormatter):
    """ETC/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(ETCBTCFormatter, self).__init__('ETC', 'BTC')


class ZECBTCFormatter(PairFormatter):
    """ZEC/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(ZECBTCFormatter, self).__init__('ZEC', 'BTC')


class DASHBTCFormatter(PairFormatter):
    """DASH/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(DASHBTCFormatter, self).__init__('DASH', 'BTC')


class BCHBTCFormatter(PairFormatter):
    """BCH/BTC PairFormatter object."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(BCHBTCFormatter, self).__init__('BCH', 'BTC')


class XRPUSDFormatter(PairFormatter):
    """XRPUSD Pairformatter."""

    def __init__(self):
        """Initialize the Formatter instance."""
        super(XRPUSDFormatter, self).__init__('XRP', 'USD')


BTCKRW = BTCKRWFormatter()
BTCUSD = BTCUSDFormatter()
ETHUSD = ETHUSDFormatter()
XMRUSD = XMRUSDFormatter()
ETCUSD = ETCUSDFormatter()
ZECUSD = ZECUSDFormatter()
DASHUSD = DASHUSDFormatter()
BCHUSD = BCHUSDFormatter()
XRPUSD = XRPUSDFormatter()

ETHBTC = ETHBTCFormatter()
LTCBTC = LTCBTCFormatter()
XMRBTC = XMRBTCFormatter()
ETCBTC = ETCBTCFormatter()
ZECBTC = ZECBTCFormatter()
DASHBTC = DASHBTCFormatter()
BCHBTC = BCHBTCFormatter()
