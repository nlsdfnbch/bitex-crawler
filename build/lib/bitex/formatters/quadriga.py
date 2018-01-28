# Import Built-ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter


log = logging.getLogger(__name__)


class QuadrigaCXFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['bid'], data['ask'], data['high'], data['low'],
                None, None, data['last'], data['volume'], None)

    @staticmethod
    def order(data, *args, **kwargs):
        return data

    @staticmethod
    def cancel(data, *args, **kwargs):
        return data

    @staticmethod
    def order_status(data, *args, **kwargs):
        return data
