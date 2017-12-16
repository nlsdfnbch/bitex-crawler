"""BitEx - Crypto-Exchange REST API Framework.

Author: Nils Diefenbach
Email: 23okrs20+github@mykolab.com
Repository at: https://github.com/nlsdfnbch/bitex
License: MIT
"""
from bitex.api.REST import BinanceREST, BitstampREST, BterREST, BitfinexREST
from bitex.api.REST import CryptopiaREST, CoincheckREST, CCEXREST
from bitex.api.REST import GDAXREST, GeminiREST
from bitex.api.REST import HitBTCREST
from bitex.api.REST import ITbitREST
from bitex.api.REST import KrakenREST
from bitex.api.REST import OKCoinREST
from bitex.api.REST import PoloniexREST
from bitex.api.REST import QuadrigaCXREST, QuoineREST
from bitex.api.REST import RockTradingREST
from bitex.api.REST import VaultoroREST
from bitex.api.REST import YunbiREST
from bitex.interface import Bter, Bitfinex, Bittrex, Bitstamp, CCEX, CoinCheck
from bitex.interface import Cryptopia, HitBTC, Kraken, OKCoin, Poloniex, QuadrigaCX
from bitex.interface import TheRockTrading, Vaultoro
from bitex.pairs import BTCUSD, ZECUSD, XMRUSD, ETCUSD, ETHUSD, DASHUSD
