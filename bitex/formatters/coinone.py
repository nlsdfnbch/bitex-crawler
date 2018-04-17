"""FormattedResponse Class for Standardized methods of the Coinone Interface class."""
# Import Built-ins
from datetime import datetime
from bitex.formatters.base import APIResponse


class CoinoneFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)

        bid = None
        ask = None
        high = data["high"]
        low = data["low"]
        last = data["last"]
        volume = data["volume"]
        timestamp = datetime.utcfromtimestamp(float(data["timestamp"]))

        return super(CoinoneFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                            timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        asks = []
        bids = []
        for i in data['ask']:
            asks.append([i['price'], i['qty']])
        for i in data['bid']:
            bids.append([i['price'], i['qty']])
        return super(CoinoneFormattedResponse, self).order_book(bids, asks, int(data['timestamp']))

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()['completeOrders']
        tradelst = []
        for trade in data:
            tradelst.append({'id': trade['timestamp'], 'price': trade['price'],
                             'qty': trade['qty'], 'time': trade['timestamp'],
                             'isBuyerMaker': None, 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(CoinoneFormattedResponse, self).trades(tradelst, datetime.utcnow())

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
        data.pop('result')
        data.pop('errorCode')
        data.pop('normalWallets')
        balances = {}
        for i in data:
            available = data[i]['avail']
            if float(available) > 0:
                balances[i.upper()] = available
        return super(CoinoneFormattedResponse, self).wallet(balances, self.received_at)
