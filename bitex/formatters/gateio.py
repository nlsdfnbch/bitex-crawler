"""FormattedResponse Class for Standardized methods of the Gateio Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse


class GateioFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)

        bid = data["highestBid"]
        ask = data["lowestAsk"]
        high = data["high24hr"]
        low = data["low24hr"]
        last = data["last"]
        volume = data["quoteVolume"]    # "quoteVolume"
        timestamp = datetime.utcnow()
        return super(GateioFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                           timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        timestamp = datetime.utcnow()
        return super(GateioFormattedResponse, self).order_book(data['bids'], data['asks'][::-1],
                                                               timestamp)

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()['data']
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['tradeID'], 'price': trade['rate'], 'qty': trade['amount'],
                             'time': float(trade['timestamp'])*1000,
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(GateioFormattedResponse, self).trades(tradelst, timestamp)

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
        data = self.json(parse_int=str, parse_float=str)['available']
        balances = {}
        for i in data:
            if (i == 'BTC') | (i == 'USD') | (float(data[i]) > 0):
                balances[i] = data[i]
        return super(GateioFormattedResponse, self).wallet(balances, self.received_at)
