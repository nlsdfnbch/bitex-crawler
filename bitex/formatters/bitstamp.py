"""FormattedResponse Class for Standardized methods of the Bitstamp Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse
from bitex.utils import timetrans


class BitstampFormattedResponse(APIResponse):
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
        return super(BitstampFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                             timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        return super(BitstampFormattedResponse, self).order_book(data['bids'], data['asks'],
                                                                 datetime.utcnow())

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['tid'], 'price': trade['price'], 'qty': trade['amount'],
                             'time': int(trade['date'])*1000, 'isBuyerMaker': trade['type'] == '0',
                             'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(BitstampFormattedResponse, self).trades(tradelst, timestamp)

    def bid(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        ts = timetrans(data['datetime'], 'datetime')
        side = 'ask' if data['type'] else 'bid'
        return super(BitstampFormattedResponse, self).bid(data['id'], data['price'], data['amount'],
                                                          side, 'N/A', ts)

    def ask(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        ts = timetrans(data['datetime'], 'datetime')
        side = 'ask' if data['type'] else 'bid'
        return super(BitstampFormattedResponse, self).ask(data['id'], data['price'], data['amount'],
                                                          side, 'N/A', ts)

    def order_status(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        ts = self.received_at_dt
        if 'id' not in data:
            extracted_data = (0, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', ts, data['reason'])
        else:
            state = data['status']
            # oid = self.method_args[0]
            oid = data['id']
            error = 'Canceled' if data['status'] == 'Canceled' else None
            extracted_data = (oid, 'N/A', 'N/A', 'N/A', 'N/A', state, ts, error)
        return super(BitstampFormattedResponse, self).order_status(*extracted_data)

    def cancel_order(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=float)
        if 'id' not in data:
            extra_data = (0, False, datetime.utcnow(), data['error'])
        else:
            extra_data = (data['id'], 'ask' if data['type'] == '1' else 'bid', datetime.utcnow())

        return super(BitstampFormattedResponse, self).cancel_order(*extra_data)

    def open_orders(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        unpacked_orders = []
        for order in data:
            side = 'ask' if order['type'] == '1' else 'bid'
            if 'pair' in self.method_kwargs:
                unpacked_order = (order['id'], self.method_kwargs['pair'], order['price'],
                                  order['amount'], side, timetrans(order['datetime'], 'timestamp'))
            else:
                unpacked_order = (order['id'], order['currency_pair'], order['price'],
                                  order['amount'], side, timetrans(order['datetime'], 'timestamp'))
            unpacked_orders.append(unpacked_order)

        ts = self.received_at
        return super(BitstampFormattedResponse, self).open_orders(unpacked_orders, ts)

    def wallet(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        balances = {}
        for i in data:
            if i[-10:] == '_available':
                available = float(data[i])
                if available > 0:
                    balances[i[:-10].upper()] = data[i]
        return super(BitstampFormattedResponse, self).wallet(balances, self.received_at)
