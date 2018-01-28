"""
Base Class for formatters. Does nothing with passed data by default;
Children should implement formatters as necessary
"""

# Import Built-Ins
import logging
from abc import ABCMeta, abstractmethod
# Import Third-Party

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


class Formatter:
    """
    ABC Class to provide formatters for `bitex.utils.return_api_response()`.
    """
    def __init__(self):
        pass

    @staticmethod
    def format_pair(input_pair):
        """
        Returns the pair properly formatted for the exchange's API.
        :param input_pair: str
        :return: str
        """
        return input_pair

    @staticmethod
    def ticker(data, *args, **kwargs):
        """
        Returns list of ticker data in following format:
            [bid_price, ask_price, high, low, open, close, last, 24h_vol, ts]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def order_book(data, *args, **kwargs):
        """
        Returns dict of lists of lists of quotes in format [ts, price, size]
        ex.:
            {'bids': [['1480941692', '0.014', '10'],
                      ['1480941690', '0.013', '0.66'],
                      ['1480941688', '0.012', '3']],
             'asks': [['1480941691', '0.015', '1'],
                      ['1480941650', '0.016', '0.67'],
                      ['1480941678', '0.017', '23']]}
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: dict
        """
        return data

    @staticmethod
    def trades(data, *args, **kwargs):
        """
        Returns list of trades in format [ts, price, size, side]
        ex.:
            [['1480941692', '0.014', '10', 'sell'],
            ['1480941690', '0.013', '0.66', 'buy'],
            ['1480941688', '0.012', '3', 'buy']]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def order(data, *args, **kwargs):
        """
        Returns the order id as str if successful, else ""
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: str
        """
        return data

    @staticmethod
    def order_status(data, *args, **kwargs):
        """
        Returns True if it exists, False if it doesn't exist
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: bool
        """
        return data

    @staticmethod
    def cancel(data, *args, **kwargs):
        """
        returns True if it was cancelled successfully, else False
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: bool
        """
        return data

    @staticmethod
    def balance(data, *args, **kwargs):
        """
        Returns dict of available balances, with currency names as keys - this ignores
        any amount already involved in a trade (i.e. margin)
        ex.:
            {'BTC': '12.04', 'LTC': '444.12'}
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: dict
        """
        return data

    @staticmethod
    def withdraw(data, *args, **kwargs):
        """
        Returns a list giving details of success and transaction details, or failure
        and reason thererof
        ex.:
            [True, currency, amount, target_address, txid]
            [False, 'Reason for failure/ error message']
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def deposit(data, *args, **kwargs):
        """
        Returns deposit address as str
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: str
        """
        return data
