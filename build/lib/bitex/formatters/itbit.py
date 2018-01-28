# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter

# Init Logging Facilities
log = logging.getLogger(__name__)


class itbtFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['bid'], data['ask'], data['high24h'], data['low24h'],
                data['openToday'], None, data['lastPrice'], data['volume24h'],
                data['serverTimeUTC'])