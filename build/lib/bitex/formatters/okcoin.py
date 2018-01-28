# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

# Init Logging Facilities
log = logging.getLogger(__name__)


class OkcnFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        date = data['date']
        data = data['ticker']
        return (data['buy'], data['sell'], data['high'], data['low'],
                None, None, data['last'], data['vol'], date)
