"""FormattedResponse Class for Standardized methods of the Bithumb Interface class."""
# Import Built-ins
from datetime import datetime

# Import third-party

# Import Home-brewed
from bitex.formatters.base import APIResponse
from bitex.utils import timetrans


class BithumbFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = (self.json(parse_int=str, parse_float=str))['data']

        bid = data["buy_price"]
        ask = data["sell_price"]
        high = data["max_price"]
        low = data["min_price"]
        last = data["closing_price"]
        volume = data["volume_1day"]
        timestamp = datetime.utcfromtimestamp(float(data["date"]) / 1000)

        return super(BithumbFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                            timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = (self.json())['data']
        asks = []
        bids = []
        for i in data['asks']:
            asks.append([i['price'], i['quantity']])
        for i in data['bids']:
            bids.append([i['price'], i['quantity']])
        return super(BithumbFormattedResponse, self).order_book(bids, asks, data['timestamp'])

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()['data']
        tradelst = []
        for trade in data:
            tradelst.append({'id': trade['cont_no'], 'price': trade['price'],
                             'qty': trade['units_traded'],
                             'time': timetrans(trade['transaction_date'], 'timestamp'),
                             'isBuyerMaker': trade['type'] == 'bid', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(BithumbFormattedResponse, self).trades(tradelst, datetime.utcnow())

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
        data = self.json(parse_int=str, parse_float=str)['data']
        balances = {}
        for i in data:
            if i[:5] == 'avail':
                available = data[i]
                if float(available) > 0:
                    balances[i.split('_')[1].upper()] = available
        return super(BithumbFormattedResponse, self).wallet(balances, self.received_at)
