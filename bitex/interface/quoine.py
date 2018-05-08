"""Quoine Interface class."""
# pylint: disable=abstract-method
# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.quoine import QuoineREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import QuoineFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class Quoine(RESTInterface):
    """Quoine Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(Quoine, self).__init__('Quoine', QuoineREST(**api_kwargs))

    # pylint: disable=arguments-differ
    def request(self, verb, endpoint, authenticate=False, **req_kwargs):
        """Request data for given endpoint from a RESTAPI object."""
        if not authenticate:
            return super(Quoine, self).request(verb, endpoint, authenticate=False, **req_kwargs)
        return super(Quoine, self).request(verb, endpoint, authenticate=True, **req_kwargs)

    def _get_supported_pairs(self):
        return [p['id'] for p in self.request('GET', 'products').json()]

    # Public Endpoints
    @check_and_format_pair
    @format_with(QuoineFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """
        Return the ticker for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/' + pair, params=kwargs)

    @check_and_format_pair
    @format_with(QuoineFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """
        Return the order book for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/{}/price_levels'.format(pair), params=kwargs)

    @check_and_format_pair
    @format_with(QuoineFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """
        Return the trades for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        params = {'product_id': pair}
        params.update(kwargs)
        return self.request('GET', 'executions', params=params)

    # Private Endpoints
    # pylint: disable=unused-argument
    def _place_order(self, pair, price, size, side, *args, **kwargs):
        params = {
            'product_id': pair,
            'side': side,
            'quantity': size,
            'price': price,
            'order_type': 'limit'
        }
        params.update(kwargs)
        return self.request('POST', 'orders', authenticate=True,
                            params={'order': params})

    @check_and_format_pair
    @format_with(QuoineFormattedResponse)
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
        return self._place_order(pair, price, size, 'sell', *args, **kwargs)

    @check_and_format_pair
    @format_with(QuoineFormattedResponse)
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
        return self._place_order(pair, price, size, 'buy', *args, **kwargs)

    @format_with(QuoineFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """
        Return the status of an order with the given id.

        :param order_id: Order ID of the order you'd like to have a status for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'orders/{}'.format(order_id), authenticate=True,
                            params=kwargs)

    @format_with(QuoineFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """
        Return all open orders.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'orders', authenticate=True, params=kwargs)

    @format_with(QuoineFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """
        Cancel the order(s) with the given id(s).

        :param order_ids: variable amount of order IDs to cancel.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        results = []
        for oid in order_ids:
            r = self.request('PUT', 'orders/{}/cancel'.format(oid), authenticate=True,
                             params=kwargs)
            results.append(r)
        return results if len(results) > 1 else results[0]

    @format_with(QuoineFormattedResponse)
    def wallet(self, *args, **kwargs):
        """
        Return the wallet of this account.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'accounts/balance', authenticate=True,
                            params=kwargs)
