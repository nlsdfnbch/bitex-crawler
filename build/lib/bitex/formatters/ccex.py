# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

# Init Logging Facilities
log = logging.getLogger(__name__)


class CcexFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['buy'], data['sell'], data['high'], data['low'], None,
                None, data['lastprice'], None, data['updated'])