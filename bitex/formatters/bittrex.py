# Import Built-ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

log = logging.getLogger(__name__)

class BtrxFormatter(Formatter):
    @staticmethod
    def order(data, *args, **kwargs):
        if data['success']:
            return data['result']['uuid']
        else:
            return False

    @staticmethod
    def order_book(data, *args, **kwargs):
        if data['success']:
            return data['result']
        else:
            return None

    @staticmethod
    def cancel(data, *args, **kwargs):
        return True if data['success'] else False