"""FormattedResponse Class for Standardized methods of the Cryptopia Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse


class CryptopiaFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        data = data["Data"]

        bid = data["BidPrice"]
        ask = data["AskPrice"]
        high = data["High"]
        low = data["Low"]
        last = data["LastPrice"]
        volume = data["Volume"]
        timestamp = datetime.utcnow()

        return super(CryptopiaFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                              timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()['Data']
        asks = []
        bids = []
        for i in data['Sell']:
            asks.append([i['Price'], i['Volume']])
        for i in data['Buy']:
            bids.append([i['Price'], i['Volume']])

        return super(CryptopiaFormattedResponse, self).order_book(bids, asks, datetime.utcnow())

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()['Data']
        tradelst = []
        for trade in data:
            tradelst.append({'id': trade['Timestamp'], 'price': trade['Price'],
                             'qty': trade['Amount'], 'time': trade['Timestamp'],
                             'isBuyerMaker': trade['Type'] == 'Buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(CryptopiaFormattedResponse, self).trades(tradelst, datetime.utcnow())

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
        data = data['Data']
        balances = {}
        for i in data:
            if (i['Symbol'] == 'BTC') or (float(i['Available']) > 0):
                balances[i['Symbol']] = i['Available']
        return super(CryptopiaFormattedResponse, self).wallet(balances, self.received_at)
