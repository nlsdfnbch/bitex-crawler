"""GDAX Interface class."""
# pylint: disable=abstract-method
# Import Built-Ins
import logging

# Import Third-party
import requests

# Import Homebrew
from bitex.api.REST.gdax import GDAXREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters.gdax import GDAXFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class GDAX(RESTInterface):
    """GDAX Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(GDAX, self).__init__('GDAX', GDAXREST(**api_kwargs))

    def _get_supported_pairs(self):
        r = requests.request('GET', 'https://api.gdax.com/products').json()
        return [x['id'] for x in r]

    # Public Endpoints
    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """
        Return the ticker for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/{}/ticker'.format(pair), params=kwargs)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """
        Return the order book for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/{}/book'.format(pair), params=kwargs)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """
        Return the trades for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/{}/trades'.format(pair), params=kwargs)

    # Private Endpoints

    def _place_order(self, pair, price, size, side, **kwargs):
        params = {'product_id': pair, 'side': side, 'size': size, 'price': price}
        params.update(kwargs)
        return self.request('POST', 'orders', json=params, authenticate=True)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """
        Place an ask order.

        :param pair: Str, pair to post order for.
        :param price: Float or str, price you'd like to ask.
        :param size: Float or str, amount of currency you'd like to sell.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self._place_order(pair, price, size, 'sell', **kwargs)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """
        Place a bid order.

        :param pair: Str, pair to post order for.
        :param price: Float or str, price you'd like to bid.
        :param size: Float or str, amount of currency you'd like to buy.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self._place_order(pair, price, size, 'buy', **kwargs)

    @format_with(GDAXFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """
        Return the status of an order with the given id.

        :param order_id: Order ID of the order you'd like to have a status for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'orders/{}'.format(order_id), authenticate=True, json=kwargs)

    @format_with(GDAXFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """
        Return all open orders.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'orders', authenticate=True, json=kwargs)

    @format_with(GDAXFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """
        Cancel the order(s) with the given id(s).

        :param order_ids: variable amount of order IDs to cancel.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        path = 'orders/{}'
        resps = []
        for oid in order_ids:
            resps.append(self.request('DELETE', path.format(oid), authenticate=True, json=kwargs))
        return resps if len(resps) > 1 else resps[0]

    @format_with(GDAXFormattedResponse)
    def wallet(self, *args, **kwargs):
        """
        Return the wallet of this account.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'accounts', authenticate=True, json=kwargs)
