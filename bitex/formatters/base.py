"""Base class for formatters."""
# Import Built-ins
import datetime
from collections import namedtuple
from abc import abstractmethod, ABCMeta

# Import third-party
import requests


# pylint: disable=super-init-not-called
class APIResponse(requests.Response, metaclass=ABCMeta):
    """The base class that each formatter has to implement.

    It adds a `formatted` property, which returns a namedtuple with data
    converted from the json response.
    """

    def __init__(self, method, response_obj, *args, **kwargs):
        """Initialize the object."""
        if not isinstance(response_obj, requests.Response):
            raise TypeError("Response obj must be requests.Response instance, not %s"
                            % type(response_obj))
        self.response = response_obj
        self.method = method
        self.method_args = args
        self.method_kwargs = kwargs
        self.received_at_dt = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        self._cached_formatted = None

    def json(self, **kwargs):
        """Wrap around response's json method to avoid None value in returned data."""
        default_kwargs = {'parse_int': str, 'parse_float': str}
        default_kwargs.update(**kwargs)
        return self.response.json(**default_kwargs)

    def __getattr__(self, attr):
        """Use methods of the encapsulated object, otherwise use what's available in the wrapper."""
        try:
            return getattr(self.response, attr)
        except AttributeError:
            return getattr(self, attr)

    @property
    def received_at(self):
        """Return APIResponse timestamp as ISO formatted string."""
        return self.received_at_dt.isoformat()

    @property
    def formatted(self):
        """Return the formatted data, extracted from the json response."""
        if not self._cached_formatted:
            self._cached_formatted = getattr(self, self.method)()
        return self._cached_formatted

    @abstractmethod
    def ticker(self, bid, ask, high, low, last, volume, ts, error=None):
        """Return namedtuple with given data."""
        ticker = namedtuple(
            "Ticker", ("bid", "ask", "high", "low", "last", "volume", "timestamp", "error"))
        return ticker(bid, ask, high, low, last, volume, ts, error)

    @abstractmethod
    def order_book(self, bids, asks, ts, error=None):
        """Return namedtuple with given data."""
        order_book = namedtuple(
            "OrderBook", ("bids", "asks", "timestamp", "error"))
        return order_book(bids, asks, ts, error)

    @abstractmethod
    def trades(self, trades, ts, error=None):
        """Return namedtuple with given data."""
        fmt_trades = namedtuple('Trades', ("trades", "timestamp", "error"))
        return fmt_trades(trades, ts, error)

    @abstractmethod
    def bid(self, oid, price, size, side, otype, ts, error=None):
        """Return namedtuple with given data."""
        bid = namedtuple(
            'Bid', ("order_id", "price", "size", "side", "order_type", "timestamp", "error"))
        return bid(oid, price, size, side, otype, ts, error)

    @abstractmethod
    def ask(self, oid, price, size, side, otype, ts, error=None):
        """Return namedtuple with given data."""
        ask = namedtuple(
            'Ask', ("order_id", "price", "size", "side", "order_type", "timestamp", "error"))
        return ask(oid, price, size, side, otype, ts, error)

    @abstractmethod
    def order_status(self, oid, price, size, side, otype, state, ts, error=None):
        """Return namedtuple with given data."""
        order_status = namedtuple('Order', ("order_id", "price", "size", "side", "order_type",
                                            "state", "timestamp", "error"))
        return order_status(oid, price, size, side, otype, state, ts, error)

    @abstractmethod
    def cancel_order(self, oid, success, timestamp, error=None):
        """Return namedtuple with given data."""
        cancelled_order = namedtuple(
            'Cancelled_Order', ("order_id", "successful", "timestamp", "error"))
        return cancelled_order(oid, success, timestamp, error)

    @abstractmethod
    def open_orders(self, orders, timestamp, error=None):
        """Return namedtuple with given data.

        An order should be the following layout:
            order = id, pair, price, size, side, ts
        """
        open_orders = namedtuple('Open_Orders', ('orders', 'timestamp', "error"))
        return open_orders(orders, timestamp, error)

    @abstractmethod
    def wallet(self, balances, timestamp, error=None):
        """Return namedtuple with given data.

        :param balances: dict of currency=value kwargs
        """
        wallet = namedtuple('Wallet', list(balances.keys()) + ['timestamp', 'error'])
        return wallet(timestamp=timestamp, error=error, **balances)
