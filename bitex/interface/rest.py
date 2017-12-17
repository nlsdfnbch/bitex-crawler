"""REST Interface base class."""
# Import Built-Ins
import logging
import abc

# Import Homebrew
from bitex.utils import check_and_format_pair
from bitex.interface.base import Interface

# Init Logging Facilities
log = logging.getLogger(__name__)


class RESTInterface(Interface):
    """REST Interface base class."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, rest_api):
        """Initialize class instance."""
        super(RESTInterface, self).__init__(name=name, rest_api=rest_api)

    # Public Endpoints
    @abc.abstractmethod
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        """
        Return the ticker for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        """
        Return the order book for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        """
        Return the trades for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    # Private Endpoints
    @abc.abstractmethod
    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        """
        Place an ask order.

        :param pair: Str, pair to post order for.
        :param price: Float or str, price you'd like to ask.
        :param size: Float or str, amount of currency you'd like to sell.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        """
        Place a bid order.

        :param pair: Str, pair to post order for.
        :param price: Float or str, price you'd like to bid.
        :param size: Float or str, amount of currency you'd like to buy.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_status(self, order_id, *args, **kwargs):
        """
        Return the status of an order with the given id.

        :param order_id: Order ID of the order you'd like to have a status for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def open_orders(self, *args, **kwargs):
        """
        Return all open orders.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_order(self, *order_ids, **kwargs):
        """
        Cancel the order(s) with the given id(s).

        :param order_ids: variable amount of order IDs to cancel.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def wallet(self, *args, **kwargs):
        """
        Return the wallet of this account.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as
                       'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        raise NotImplementedError
