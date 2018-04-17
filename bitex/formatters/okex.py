"""FormattedResponse Class for Standardized methods of the OKex Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse


class OKexFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        bid = data["ticker"]["buy"]
        ask = data["ticker"]["sell"]
        high = data["ticker"]["high"]
        low = data["ticker"]["low"]
        last = data["ticker"]["last"]
        volume = data["ticker"]["vol"]
        timestamp = datetime.utcfromtimestamp(float(data["date"]))

        return super(OKexFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                         timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        return super(OKexFormattedResponse, self).order_book(data['bids'], data['asks'][::-1],
                                                             datetime.utcnow())

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        tradelst = []
        timestamp = datetime.utcnow()
        for trade in data:
            tradelst.append({'id': trade['tid'], 'price': trade['price'],
                             'qty': trade['amount'], 'time': trade['date_ms'],
                             'isBuyerMaker': trade['type'] == 'buy', 'isBestMatch': None})
            # what meaning isBuyerMaker is? if we should remain it in all trades formatter?
            # raise NotImplementedError
        return super(OKexFormattedResponse, self).trades(tradelst, timestamp)

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
        data = self.json(parse_int=str, parse_float=str)['info']['funds']['free']
        balances = {}
        for i in data:
            if i[0] != '1' and (float(data[i]) > 0 or i == 'btc' or i == 'eth' or i == 'ltc'):
                balances[i.upper()] = data[i]
        return super(OKexFormattedResponse, self).wallet(balances, self.received_at)
