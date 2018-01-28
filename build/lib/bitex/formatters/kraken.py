# Import Built-ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter


log = logging.getLogger(__name__)


class KrknFormatter(Formatter):

    @staticmethod
    def format_pair(input_pair):
        """
        Formats input to conform with kraken pair format. The API expects one of
        two formats:
        XBTXLT
        or
        XXBTXLTC

        Where crypto currencies have an X prepended, and fiat currencies have
        a Z prepended. Since the API returns the 8 character format, that's what
        we will format into as well.

        We expect 6 or 8 character strings, but do not explicitly check for it.
        Should the string be of uneven length, we'll split the pair in the middle
        like so:
        BTC-LTC -> BTC, LTC.

        Furthermore, since Kraken uses 'XBT' as Bitcoins symbol, we look for, and
        replace occurrences of 'btc' with 'XBT'.

        :param input_pair: str
        :return: str
        """
        if len(input_pair) % 2 == 0:
            base_cur, quote_cur = input_pair[:len(input_pair)//2], input_pair[len(input_pair)//2:]
        else:
            base_cur, quote_cur = input_pair.split(input_pair[len(input_pair)//2])

        def add_prefix(input_string):
            input_string = input_string.lower()
            if any(x in input_string for x in ['usd', 'eur', 'jpy', 'gbp', 'cad']):
                # appears to be fiat currency
                if not input_string.startswith('z'):
                    input_string = 'z' + input_string

            else:
                # Appears to be Crypto currency
                if 'btc' in input_string:
                    input_string = input_string.replace('btc', 'xbt')

                if not input_string.startswith('x') or len(input_string) == 3:
                    input_string = 'x' + input_string
            return input_string

        base_cur = add_prefix(base_cur)
        quote_cur = add_prefix(quote_cur)

        return (base_cur + quote_cur).upper()

    @staticmethod
    def ticker(data, *args, **kwargs):
        tickers = []
        for k in data['result']:
            d = data['result'][k]
            tickers.append((d['b'][0], d['a'][0], d['h'][1], d['l'][1], d['o'],
                           None, d['c'][0], d['v'][1], None))
        if len(tickers) > 1:
            return tickers
        else:
            return tickers[0]

    @staticmethod
    def order(data, *args, **kwargs):
        if not data['error']:
            return data['result']['txid']
        else:
            return False

    @staticmethod
    def order_book(data, *args, **kwargs):
        pair = args[1]
        forex = ['EUR', 'USD', 'GBP', 'JPY', 'CAD']
        if len(pair) == 6:
            base_cur = pair[:3]
            quote_cur = pair[3:]
            if base_cur.upper() in forex:
                base_cur = 'Z' + base_cur
            else:
                base_cur = 'X' + base_cur

            if quote_cur.upper() in forex:
                quote_cur = 'Z' + quote_cur
            else:
                quote_cur = 'X' + quote_cur
            return data['result'][base_cur+quote_cur]
        else:
            return data['result'][pair]

    @staticmethod
    def cancel(data, *args, **kwargs):
        if int(data['result']['count']) == 1:
            return True
        else:
            return False
