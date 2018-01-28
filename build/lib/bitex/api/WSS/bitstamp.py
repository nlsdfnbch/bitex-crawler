# Import Built-Ins
import logging

# Import Third-Party
import pusherclient

# Import Homebrew
from bitex.api.WSS.base import WSSAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class BitstampWSS(WSSAPI):
    """
    Creates a BitstampWSS Object, which automatically describes to all
    available endpoints of the  Bitstamp Websocket API.

    By Default, data is printed to stdout. If you'd like to customize this
    behaviour, subclass this class, and overwrite the *_callback() methods.

    If you need to have per-channel customization, you will have to overwrite
    the _register_*_channel() methods accordingly.
    """
    def __init__(self, key=None, exclude=None, include_only=None, **kwargs):
        """
        Initializes Instance.

        Pusher Class Attributes:
        :param key: Pusher key, str; stored in self.addr
        :param kwargs: Keyword arguments passed to pusher object.
        """

        key = key if key else 'de504dc5763aeef9ff52'

        super(BitstampWSS, self).__init__(key, 'Bitstamp')

        self.pusher = None
        self.__pusher_options = kwargs

        self.channels = ['live_trades', 'live_trades_btceur',
                         'live_trades_eurusd', 'live_trades_xrpusd',
                         'live_trades_xrpeur', 'live_trades_xrpbtc',
                         'order_book_btceur', 'order_book_eurusd',
                         'order_book_xrpusd', 'order_book_xrpeur',
                         'order_book_xrpbtc', 'diff_order_book', 'order_book',
                         'diff_order_book_btceur', 'diff_order_book_eurusd',
                         'diff_order_book_xrpusd', 'diff_order_book_xrpeur',
                         'diff_order_book_xrpbtc', 'live_orders',
                         'live_orders_btceur', 'live_orders_eurusd',
                         'live_orders_xrpusd', 'live_orders_xrpeur',
                         'live_orders_xrpbtc']
        if include_only:
            if all(x in self.channels for x in include_only):
                self.channels = include_only
            else:
                raise ValueError("'include_only: must be a list of strings of"
                                 "valid channel name! %s" % self.channels)
        if exclude:
            if all(x in self.channels for x in exclude):
                for x in exclude:
                    self.channels.remove(x)
            else:
                raise ValueError("'exclude: must be a list of strings of"
                                 "valid channel name! %s" % self.channels)

    def start(self):
        """
        Extension of Pusher.connect() method, which registers all callbacks with
        the relevant channels, before initializing a connection.
        :return:
        """
        super(BitstampWSS, self).start()

        self.pusher = pusherclient.Pusher(self.addr, **self.__pusher_options)
        self.pusher.connection.bind('pusher:connection_established',
                                    self._register_bindings)
        self.pusher.connect()

    def stop(self):
        super(BitstampWSS, self).stop()
        self.pusher = None

    """
    Custom Callbacks
    """

    def live_trades_callback(self, pair, data):
        """
        This callback is called when data from the live_trades channel is
        received. Overwrite this in children, to change the way data is handled.
        if you require per-pair customization, see the pair-specific callbacks.
        :param pair:
        :param data:
        :return:
        """
        self.data_q.put(('live_trades', pair, data))

    def btcusd_lt_callback(self, data):
        self.live_trades_callback('BTCUSD', data)

    def btceur_lt_callback(self, data):
        self.live_trades_callback('BTCEUR', data)

    def eurusd_lt_callback(self, data):
        self.live_trades_callback('EURUSD', data)

    def xrpusd_lt_callback(self, data):
        self.live_trades_callback('XRPUSD', data)

    def xrpeur_lt_callback(self, data):
        self.live_trades_callback('XRPEUR', data)

    def xrpbtc_lt_callback(self, data):
        self.live_trades_callback('XRPBTC', data)

    """
    Custom Order Book Callback
    """

    def order_book_callback(self, pair, data):
        """
        This callback is called when data from the order_book channel is
        received.
        :param data:
        :return:
        """
        self.data_q.put(('order_book', pair, data))

    def btcusd_ob_callback(self, data):
        self.order_book_callback('BTCUSD', data)

    def btceur_ob_callback(self, data):
        self.order_book_callback('BTCEUR', data)

    def eurusd_ob_callback(self, data):
        self.order_book_callback('EURUSD', data)

    def xrpusd_ob_callback(self, data):
        self.order_book_callback('XRPUSD', data)

    def xrpeur_ob_callback(self, data):
        self.order_book_callback('XRPEUR', data)

    def xrpbtc_ob_callback(self, data):
        self.order_book_callback('XRPBTC', data)

    """
    Custom Diff Order Book Callback
    """

    def diff_order_book_callback(self, pair, data):
        """
        This callback is called when data from the diff_order_book channel is
        received.
        :param pair:
        :param data:
        :return:
        """
        self.data_q.put(('diff_order_book', pair, data))

    def btcusd_dob_callback(self, data):
        self.diff_order_book_callback('BTCUSD', data)

    def btceur_dob_callback(self, data):
        self.diff_order_book_callback('BTCEUR', data)

    def eurusd_dob_callback(self, data):
        self.diff_order_book_callback('EURUSD', data)

    def xrpusd_dob_callback(self, data):
        self.diff_order_book_callback('XRPUSD', data)

    def xrpeur_dob_callback(self, data):
        self.diff_order_book_callback('XRPEUR', data)

    def xrpbtc_dob_callback(self, data):
        self.diff_order_book_callback('XRPBTC', data)

    """
    Custom Live Orders Callback
    """

    def live_orders_callback(self, pair, data):
        """
        This callback is called when data from the live_orders channel is
        received.
        :param pair:
        :param data:
        :return:
        """
        self.data_q.put(('live_orders', pair, data))

    def btcusd_lo_callback(self, data):
        self.live_orders_callback('BTCUSD', data)

    def btceur_lo_callback(self, data):
        self.live_orders_callback('BTCEUR', data)

    def eurusd_lo_callback(self, data):
        self.live_orders_callback('EURUSD', data)

    def xrpusd_lo_callback(self, data):
        self.live_orders_callback('XRPUSD', data)

    def xrpeur_lo_callback(self, data):
        self.live_orders_callback('XRPEUR', data)

    def xrpbtc_lo_callback(self, data):
        self.live_orders_callback('XRPBTC', data)

    """
    Register Methods
    """

    def _register_bindings(self, data):
        """
        connection_handler method which is called when we connect to pusher.
        Responsible for binding callbacks to channels before we connect.
        :return:
        """
        self._register_diff_order_book_channels()
        self._register_live_orders_channels()
        self._register_live_trades_channels()
        self._register_order_book_channels()

    def _bind_channels(self, events, channels):
        """
        Binds given channel events to callbacks.
        :param events: str or list
        :param channels: dict of channel_name: callback_method() pairs
        :return:
        """
        for channel_name in channels:
            if channel_name in self.channels:
                channel = self.pusher.subscribe(channel_name)
                if isinstance(events, list):
                    for event in events:
                        channel.bind(event, channels[channel_name])
                else:
                    channel.bind(events, channels[channel_name])

    def _register_live_trades_channels(self):
        """
        Registers the binding for the live_trades_channels channels.
        :return:
        """

        channels = {'live_trades': self.btcusd_lt_callback,
                    'live_trades_btceur': self.btceur_lt_callback,
                    'live_trades_eurusd': self.eurusd_lt_callback,
                    'live_trades_xrpusd': self.xrpusd_lt_callback,
                    'live_trades_xrpeur': self.xrpeur_lt_callback,
                    'live_trades_xrpbtc': self.xrpbtc_lt_callback}

        event = 'trade'
        self._bind_channels(event, channels)

    def _register_order_book_channels(self):
        """
        Registers the binding for the order_book channels.
        :return:
        """
        channels = {'order_book': self.btcusd_ob_callback,
                    'order_book_btceur': self.btceur_ob_callback,
                    'order_book_eurusd': self.eurusd_ob_callback,
                    'order_book_xrpusd': self.xrpusd_ob_callback,
                    'order_book_xrpeur': self.xrpeur_ob_callback,
                    'order_book_xrpbtc': self.xrpbtc_ob_callback}

        event = 'data'
        self._bind_channels(event, channels)

    def _register_diff_order_book_channels(self):
        """
        Registers the binding for the diff_order_book channels.
        :return:
        """
        channels = {'diff_order_book': self.btcusd_dob_callback,
                    'diff_order_book_btceur': self.btceur_dob_callback,
                    'diff_order_book_eurusd': self.eurusd_dob_callback,
                    'diff_order_book_xrpusd': self.xrpusd_dob_callback,
                    'diff_order_book_xrpeur': self.xrpeur_dob_callback,
                    'diff_order_book_xrpbtc': self.xrpbtc_dob_callback}

        event = 'data'
        self._bind_channels(event, channels)

    def _register_live_orders_channels(self):
        channels = {'live_orders': self.btcusd_lo_callback,
                    'live_orders_btceur': self.btceur_lo_callback,
                    'live_orders_eurusd': self.eurusd_lo_callback,
                    'live_orders_xrpusd': self.xrpusd_lo_callback,
                    'live_orders_xrpeur': self.xrpeur_lo_callback,
                    'live_orders_xrpbtc': self.xrpbtc_lo_callback}

        events = ['order_created', 'order_changed', 'order_deleted']
        self._bind_channels(events, channels)
