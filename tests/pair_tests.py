# Import Built-Ins
import logging
import unittest
# Import Third-Party

# Import Homebrew
from bitex.pairs import PairFormatter
# Init Logging Facilities
log = logging.getLogger(__name__)


class PairTests(unittest.TestCase):
    def test_that_pair_class_returns_correct_format_for(self):
        pair = PairFormatter('BTC', 'USD')
        # Assert All exchanges are supported and format correctly;
        # This excludes edge cases, which are tested separately
        self.assertEqual(pair.format_for('Kraken'), 'XXBTZUSD')
        self.assertEqual(pair.format_for('Bitstamp'), 'btcusd')
        self.assertEqual(pair.format_for('Bitfinex'), 'BTCUSD')
        self.assertEqual(pair.format_for('CoinCheck'), 'btc_usd')
        self.assertEqual(pair.format_for('GDAX'), 'BTC-USD')
        self.assertEqual(pair.format_for('ITBit'), 'XBTUSD')
        self.assertEqual(pair.format_for('OKCoin'), 'btc_usd')
        self.assertEqual(pair.format_for('C-CEX'), 'btc-usd')
        self.assertEqual(pair.format_for('Cryptopia'), 'BTC_USD')
        self.assertEqual(pair.format_for('Gemini'), 'btcusd')
        self.assertEqual(pair.format_for('Yunbi'), 'btcusd')
        self.assertEqual(pair.format_for('The Rock Trading Ltd.'), 'BTCUSD')
        self.assertEqual(pair.format_for('Quoine'), 'BTCUSD')
        self.assertEqual(pair.format_for('QuadrigaCX'), 'btc_usd')
        self.assertEqual(pair.format_for('HitBTC'), 'BTCUSD')
        self.assertEqual(pair.format_for('Vaultoro'), 'BTC-USD')
        self.assertEqual(pair.format_for('Bter'), 'btc_usd')
        self.assertEqual(pair.format_for('CEXio'), 'BTCUSD')
        self.assertEqual(pair.format_for('Exmo'), 'BTC_USD')
        self.assertEqual(pair.format_for('Bithumb'), 'BTC')	# only fiat is KRW
        self.assertEqual(pair.format_for('Coinone'), 'btc')	# only fiat is KRW
        self.assertEqual(pair.format_for('Coinnest'), 'btc')	# only fiat is KRW

        # Assert that calling the formatter returns the standard presentation
        self.assertEqual(str(pair), 'BTCUSD')

        pair = PairFormatter('BTC', 'USDT')
        self.assertEqual(pair.format_for('Binance'), 'BTCUSDT')  # Binance had no BTCUSD, but do not trans BTCUSD to BTCUSDT
        self.assertEqual(pair.format_for('Bittrex'), 'USDT-BTC')
        self.assertEqual(pair.format_for('Poloniex'), 'USDT_BTC')
        self.assertEqual(pair.format_for('Gateio'), 'btc_usdt')

    def test_poloniex_formatter_edge_case(self):
        # Assert that BTC in quote is swapped to base
        pair = PairFormatter('LTC', 'BTC')
        self.assertEqual(pair.format_for('Poloniex'), 'BTC_LTC')

        # Assert that USDT is swapped from quote to base
        pair = PairFormatter('LTC', 'USDT')
        self.assertEqual(pair.format_for('Poloniex'), 'USDT_LTC')

        # Assert that XMR is only swapped to base if current base is not BTC or
        # USDT
        pair = PairFormatter('BTC', 'XMR')
        self.assertEqual(pair.format_for('Poloniex'), 'BTC_XMR')
        pair = PairFormatter('USDT', 'XMR')
        self.assertEqual(pair.format_for('Poloniex'), 'USDT_XMR')
        pair = PairFormatter('ETH', 'XMR')
        self.assertEqual(pair.format_for('Poloniex'), 'XMR_ETH')

    def test_bitfinex_formatter_edge_case(self):
        # The DASH symbol is shortened in the Bitfinex API standard, hence
        # our formatter should take this into consideration
        pair = PairFormatter('DASH', 'USD')
        self.assertEqual(pair.format_for('Bitfinex'), 'DSHUSD')

        pair = PairFormatter('USD', 'DASH')
        self.assertEqual(pair.format_for('Bitfinex'), 'USDDSH')

    def test_kraken_formatter_edge_case(self):
        pair = PairFormatter('BCH', 'EUR')
        self.assertEqual(pair.format_for('Kraken'), 'BCHEUR')

if __name__ == '__main__':
    unittest.main(verbosity=2)
