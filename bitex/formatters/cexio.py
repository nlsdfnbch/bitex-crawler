"""FormattedResponse Class for Standardized methods of the CEXio Interface class."""
from datetime import datetime
from bitex.formatters.base import APIResponse


class CEXioFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)

        bid = data["bid"]
        ask = data["ask"]
        high = data["high"]
        low = data["low"]
        last = data["last"]
        volume = data["volume"]
        timestamp = datetime.utcfromtimestamp(float(data["timestamp"]))

        return super(CEXioFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                          timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        return super(CEXioFormattedResponse, self).order_book(data['bids'], data['asks'],
                                                              int(data['timestamp']))

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['tid'], 'price': trade['price'],
                             'qty': trade['amount'], 'time': int(trade['date']) * 1000,
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(CEXioFormattedResponse, self).trades(tradelst, timestamp)

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
        data = self.json(parse_int=str, parse_float=str)
        data.pop('timestamp')
        data.pop('username')
        balances = {}
        for i in data:
            available = data[i]['available']
            if float(available) > 0:
                balances[i] = available
        return super(CEXioFormattedResponse, self).wallet(balances, self.received_at)
