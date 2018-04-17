"""FormattedResponse Class for Standardized methods of the Bittrex Interface class."""
# Import Built-ins
from datetime import datetime

# Import third-party
import pytz

# Import Home-brewed
from bitex.formatters.base import APIResponse
from bitex.utils import timetrans


class BittrexFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        data = data["result"][0]

        dt_str = data["TimeStamp"]
        curr_timestamp = pytz.utc.localize(datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f'))

        bid = data["Bid"]
        ask = data["Ask"]
        high = data["High"]
        low = data["Low"]
        last = data["Last"]
        volume = data["Volume"]
        timestamp = curr_timestamp

        return super(BittrexFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                            timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()['result']
        asks = []
        bids = []
        for i in data['sell']:
            asks.append([i['Rate'], i['Quantity']])
        for i in data['buy']:
            bids.append([i['Rate'], i['Quantity']])

        return super(BittrexFormattedResponse, self).order_book(bids, asks, datetime.utcnow())

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()['result']
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['Id'], 'price': trade['Price'], 'qty': trade['Quantity'],
                             'time': timetrans(trade['TimeStamp'], 'timestamp')*1000,
                             'isBuyerMaker': trade['OrderType'] == 'BUY', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(BittrexFormattedResponse, self).trades(tradelst, timestamp)

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
        data = self.json(parse_int=str, parse_float=str)['result']
        balances = {}
        for i in data:
            balances[i['Currency']] = i['Available']

        return super(BittrexFormattedResponse, self).wallet(balances, self.received_at)
