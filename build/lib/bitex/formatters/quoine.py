# Import Built-ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.formatters.base import Formatter


log = logging.getLogger(__name__)


class QoinFormatter(Formatter):

    @staticmethod
    def ticker(data, *args, **kwargs):
        return (data['market_bid'], data['market_ask'], data['high_market_ask'],
                data['low_market_bid'], None, None, data['last_traded_price'],
                data['volume_24h'], None)

    @staticmethod
    def order(data, *args, **kwargs):
        return data

    @staticmethod
    def cancel(data, *args, **kwargs):
        return data

    @staticmethod
    def order_status(data, *args, **kwargs):
        return data
