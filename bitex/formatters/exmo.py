"""FormattedResponse Class for Standardized methods of the Exmo Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse


class ExmoFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        pair = self.method_args[1]
        data = self.json(parse_int=str, parse_float=str)[pair]

        bid = data["buy_price"]
        ask = data["sell_price"]
        high = data["high"]
        low = data["low"]
        last = data["last_trade"]
        volume = data["vol"]
        timestamp = datetime.utcfromtimestamp(float(data["updated"]))
        return super(ExmoFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                         timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        pair = self.method_args[1]
        data = self.json()[pair]
        timestamp = datetime.utcnow()
        return super(ExmoFormattedResponse, self).order_book(data['bid'], data['ask'], timestamp)

    def trades(self):
        """Return namedtuple with given data."""
        pair = self.method_args[1]
        data = self.json()[pair]
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['trade_id'], 'price': trade['price'],
                             'qty': trade['quantity'], 'time': int(trade['date']) * 1000,
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(ExmoFormattedResponse, self).trades(tradelst, timestamp)

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
        data = self.json(parse_int=str, parse_float=str)['balances']
        balances = {}
        for i in data:
            if (i == 'BTC') | (i == 'USD') | (float(data[i]) > 0):
                balances[i] = data[i]
        return super(ExmoFormattedResponse, self).wallet(balances, self.received_at)
