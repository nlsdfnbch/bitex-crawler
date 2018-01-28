# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

# Init Logging Facilities
log = logging.getLogger(__name__)


class GmniFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['bid'], data['ask'], None, None, None, None, data['last'],
                data['volume'][args[0][:3].upper()], data['volume']['time'])