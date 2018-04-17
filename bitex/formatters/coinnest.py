"""FormattedResponse Class for Standardized methods of the Coinnest Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse


class CoinnestFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)

        bid = data["buy"]
        ask = data["sell"]
        high = data["high"]
        low = data["low"]
        last = data["last"]
        volume = data["vol"]
        timestamp = datetime.utcfromtimestamp(int(data["time"]))
        return super(CoinnestFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                             timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        return super(CoinnestFormattedResponse, self).order_book(data['bids'], data['asks'],
                                                                 datetime.utcnow())

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        for trade in data:
            tradelst.append({'id': trade['tid'], 'price': trade['price'], 'qty': trade['amount'],
                             'time': trade['date'],
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(CoinnestFormattedResponse, self).trades(tradelst, datetime.utcnow())

    def bid(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def ask(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def order_status(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def open_orders(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def cancel_order(self):
        """Return namedtuple with given data."""
        raise NotImplementedError

    def wallet(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        balances = {}
        for i in data:
            if i[-8:] == '_balance':
                if (i[:-8] == 'btc') | (i[:-8] == 'krw') | (float(data[i]) > 0):
                    balances[i[:-8].upper()] = data[i]
        return super(CoinnestFormattedResponse, self).wallet(balances, self.received_at)
