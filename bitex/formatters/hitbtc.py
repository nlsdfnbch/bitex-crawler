"""FormattedResponse Class for Standardized methods of the HitBTC Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse
from bitex.utils import timetrans
from bitex.exceptions import PublicDataFetchError


class HitBTCFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        if not self.ok:
            raise PublicDataFetchError(self.ok,self.status_code,self.reason)
        data = self.json(parse_int=str, parse_float=str)
        bid = data["bid"]
        ask = data["ask"]
        high = data["high"]
        low = data["low"]
        last = data["last"]
        volume = data["volume"]
        timestamp = datetime.strptime(data['timestamp'][:-5], "%Y-%m-%dT%H:%M:%S")

        return super(HitBTCFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                           timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        if 'asks' in data:  # api version 1
            bids = data['bids']
            asks = data['asks']
        else:        # api version 2
            asks = []
            bids = []
            for i in data['ask']:
                asks.append([i['price'], i['size']])
            for i in data['bid']:
                bids.append([i['price'], i['size']])

        timestamp = datetime.utcnow()
        return super(HitBTCFormattedResponse, self).order_book(bids, asks, timestamp)

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['id'], 'price': trade['price'], 'qty': trade['quantity'],
                             'time': timetrans(trade['timestamp'], 'timestamp')*1000,
                             'isBuyerMaker': trade['side'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(HitBTCFormattedResponse, self).trades(tradelst, timestamp)

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
        balances = {}
        for i in data:
            available = i['available']
            if (float(available) > 0) | (i['currency'] == 'BTC'):
                balances[i['currency']] = available
        return super(HitBTCFormattedResponse, self).wallet(balances, self.received_at)
