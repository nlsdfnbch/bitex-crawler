"""FormattedResponse Class for Standardized methods of the Bitfinex Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse
from bitex.exceptions import PublicDataFetchError


class BitfinexFormattedResponse(APIResponse):
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
        last = data["last_price"]
        volume = data["volume"]
        timestamp = datetime.utcfromtimestamp(float(data["timestamp"]))

        return super(BitfinexFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                             timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        asks = []
        bids = []
        if 'bids' in data:  # api version 1
            for i in data['asks']:
                asks.append([i['price'], i['amount']])
            for i in data['bids']:
                bids.append([i['price'], i['amount']])
        else:   # api version 2
            for i in data:
                if i[2][1] == '-':
                    bids.append([i[0], i[2]])
                else:
                    asks.append([i[0], i[2][1:]])
        timestamp = datetime.utcnow()
        return super(BitfinexFormattedResponse, self).order_book(bids, asks, timestamp)

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['tid'], 'price': trade['price'],
                             'qty': trade['amount'], 'time': trade['timestamp']+'000',
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(BitfinexFormattedResponse, self).trades(tradelst, timestamp)

    def bid(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        ts = datetime.utcfromtimestamp(float(data["timestamp"]))
        side = 'ask' if data['side'] == 'sell' else 'bid'
        return super(BitfinexFormattedResponse, self).bid(data['id'], data['price'],
                                                          data['remaining_amount'], side,
                                                          data['type'], ts)

    def ask(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        ts = datetime.utcfromtimestamp(float(data["timestamp"]))
        side = 'ask' if data['side'] == 'sell' else 'bid'
        return super(BitfinexFormattedResponse, self).bid(data['id'], data['price'],
                                                          data['remaining_amount'], side,
                                                          data['type'], ts)

    def order_status(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        if 'id' not in data:
            extracted_data = (0, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', datetime.utcnow(),
                              data['message'])
        else:
            # oid = self.method_args[0]
            side = 'ask' if data['side'] == 'sell' else 'bid'
            state = 'is_live' if data['is_live'] else 'is_not_live'
            ts = datetime.utcfromtimestamp(float(data['timestamp']))
            error = 'is_cancelled' if data['is_cancelled'] else None
            extracted_data = (data['id'], data['price'], data['remaining_amount'],
                              side, data['type'], state, ts, error)
        return super(BitfinexFormattedResponse, self).order_status(*extracted_data)

    def cancel_order(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=float)
        if 'id' not in data:
            extracted_data = (0, False, None, data['message'])
        else:
            extracted_data = (data['id'], 'ask' if data['side'] == 'sell' else 'bid',
                              datetime.utcnow())

        return super(BitfinexFormattedResponse, self).cancel_order(*extracted_data)

    def open_orders(self):  # 'Open_Orders', ('orders', 'timestamp', "error")
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        unpacked_orders = []
        for order in data:
            side = 'ask' if order['side'] == 'sell' else 'bid'
            if 'pair' in self.method_kwargs:
                unpacked_order = (order['id'], self.method_kwargs['pair'], order['price'],
                                  order['remaining_amount'], side, order['timestamp'])
            else:
                unpacked_order = (order['id'], order['symbol'], order['price'],
                                  order['remaining_amount'], side, order['timestamp'])
            unpacked_orders.append(unpacked_order)

        ts = self.received_at
        return super(BitfinexFormattedResponse, self).open_orders(unpacked_orders, ts)

    def wallet(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        balances = {(d['currency']).upper(): d['amount'] for d in data}
        return super(BitfinexFormattedResponse, self).wallet(balances, self.received_at)
