import logging
logging.getLogger(__name__).warning("The API clients available in this package are deprecated "
                                    "and will be no longer available in their current form "
                                    "starting with version 2.0!")
from bitex.interfaces import Kraken, Bitfinex, Bitstamp, CCEX, Coincheck
from bitex.interfaces import Cryptopia, Gemini, ItBit, OKCoin, RockTradingLtd
from bitex.interfaces import Yunbi, Bittrex, Poloniex, Quoine, QuadrigaCX
from bitex.interfaces import Vaultoro, HitBtc, Bter, GDAX

