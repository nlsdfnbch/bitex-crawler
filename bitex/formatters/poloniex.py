"""FormattedResponse Class for Standardized methods of the Poloniex Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse
from bitex.utils import timetrans


class PoloniexFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        # The Poloniex public ticker returns a json containing the ticker of all the pairs traded
        # on the exchange. This is why we had to store the arguments passed to the method (ticker,
        # ask, etc..) of the Poloniex class, in order to extract the pair the user wants, and
        # format it in the correct way.
        all_pairs_tickers = self.json(parse_int=str, parse_float=str)
        _, pair_requested = self.method_args[:2]

        data = all_pairs_tickers[pair_requested]
        bid = data["highestBid"]
        ask = data["lowestAsk"]
        high = data["high24hr"]
        low = data["low24hr"]
        last = data["last"]
        volume = data["quoteVolume"]
        timestamp = datetime.utcnow()
        return super(PoloniexFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                             timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        return super(PoloniexFormattedResponse, self).order_book(data['bids'], data['asks'],
                                                                 timetrans('now', 'timestamp'))

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['tradeID'], 'price': trade['rate'], 'qty': trade['amount'],
                             'time': int(timetrans(trade['date'], 'timestamp') * 1000),
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(PoloniexFormattedResponse, self).trades(tradelst, timestamp)

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
