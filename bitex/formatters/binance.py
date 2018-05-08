"""FormattedResponse Class for Standardized methods of the Binance Interface class."""
# Import Built-ins
from datetime import datetime

# Import Home-brewed
from bitex.formatters.base import APIResponse


class BinanceFormattedResponse(APIResponse):
    """FormattedResponse class.

    Returns the standardized method's json results as a formatted data in a namedTuple.
    """

    def ticker(self):
        """Return namedtuple with given data."""
        data = self.json(parse_int=str, parse_float=str)
        bid = data["bidPrice"]
        ask = data["askPrice"]
        high = data["highPrice"]
        low = data["lowPrice"]
        last = data["lastPrice"]
        volume = data["volume"]
        timestamp = datetime.utcnow()
        return super(BinanceFormattedResponse, self).ticker(bid, ask, high, low, last, volume,
                                                            timestamp)

    def order_book(self):
        """Return namedtuple with given data."""
        data = self.json()
        bids = data['bids']
        asks = data['asks']
        timestamp = datetime.utcnow()
        return super(BinanceFormattedResponse, self).order_book(bids, asks, timestamp)

    def trades(self):
        """Return namedtuple with given data."""
        data = self.json()
        trades = data
        timestamp = datetime.utcnow()
        return super(BinanceFormattedResponse, self).trades(trades, timestamp)

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
        # balances = {d['asset']: d['free'] for d in data}
        balances = {}
        for i in data:
            available = i['free']
            if float(available) > 0:
                balances[i['asset']] = available
        return super(BinanceFormattedResponse, self).wallet(balances, self.received_at)
