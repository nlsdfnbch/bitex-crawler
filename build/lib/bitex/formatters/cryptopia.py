# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

# Init Logging Facilities
log = logging.getLogger(__name__)


class CrptFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['BidPrice'], data['AskPrice'], data['High'], data['Low'],
                None, None, data['LastPrice'], None, data['timestamp'])