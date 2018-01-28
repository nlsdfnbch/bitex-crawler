# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

# Init Logging Facilities
log = logging.getLogger(__name__)


class GdaxFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['bid'], data['ask'], None, None, None, None, data['price'],
                data['volume'], data['time'])