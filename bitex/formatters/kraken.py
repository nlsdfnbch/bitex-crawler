"""FormattedResponse Class for Standardized methods of the Kraken Interface class."""
# Import Built-Ins
from datetime import datetime

# Import Third-party

# Import home-brew
from bitex.formatters.base import APIResponse


class KrakenFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        pair = self.method_args[1]
        data = self.json(parse_int=str, parse_float=str)['result'][pair]
        bid = data["b"][0]
        ask = data["a"][0]
        high = data["h"][1]
        low = data["l"][1]
        last = data["c"][0]
        volume = data["v"][1]
        timestamp = datetime.utcnow()
        return super(KrakenFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                           timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        pair = self.method_args[1]
        data = self.json()['result'][pair]
        bids = data['bids']
        asks = data['asks']
        timestamp = datetime.utcnow()
        return super(KrakenFormattedResponse, self).order_book(bids, asks, timestamp)

    def trades(self):
        """Return namedtuple with given data."""
        pair = self.method_args[1]
        data = self.json()['result'][pair]
        tradelst = []
        for trade in data:
            tradelst.append({'id': trade[2].replace('.', ''), 'price': trade[0],
                             'qty': trade[1], 'time': trade[2],
                             'isBuyerMaker': trade[3] != 's', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(KrakenFormattedResponse, self).trades(tradelst, datetime.utcnow())

    def bid(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def ask(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def order_status(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def cancel_order(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def open_orders(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def wallet(self):
        """Return namedtuple with given data."""
        raise NotImplementedError
