# Import Built-Ins
import logging
import json
import time
import queue
import threading
from threading import Thread

# Import Third-Party
from websocket import create_connection, WebSocketTimeoutException
from websocket import WebSocketConnectionClosedException

# Import Homebrew
from bitex.api.WSS.base import WSSAPI

# import Server-side Exceptions
from bitex.api.WSS.exceptions import InvalidBookLengthError, GenericSubscriptionError
from bitex.api.WSS.exceptions import NotSubscribedError,  AlreadySubscribedError
from bitex.api.WSS.exceptions import InvalidPairError, InvalidChannelError
from bitex.api.WSS.exceptions import InvalidEventError, InvalidBookPrecisionError

# import Client-side Exceptions
from bitex.api.WSS.exceptions import UnknownEventError, UnknownWSSError
from bitex.api.WSS.exceptions import UnknownWSSInfo, AlreadyRegisteredError
from bitex.api.WSS.exceptions import NotRegisteredError, UnknownChannelError
from bitex.api.WSS.exceptions import FaultyPayloadError

# Init Logging Facilities
log = logging.getLogger(__name__)


class BitfinexWSS(WSSAPI):
    """
    Client Class to connect to Bitfinex Websocket API. Data is stored in attributes.
    Features error handling and logging, as well as reconnection automation if
    the Server issues a connection reset.
    """

    def __init__(self, pairs=None):
        """
        Initializes BitfinexWSS Instance.
        :param key: Api Key as string
        :param secret: Api secret as string
        :param addr: Websocket API Address
        """
        super(BitfinexWSS, self).__init__('wss://api.bitfinex.com/ws/2', 'Bitfinex')
        self.conn = None
        if pairs:
            self.pairs = pairs
        else:
            self.pairs = ['ETHBTC', 'BTCUSD', 'ETHUSD', 'ETCUSD', 'ETCBTC',
                          'ZECUSD', 'ZECBTC', 'XMRUSD', 'XMRBTC', 'LTCUSD',
                          'LTCBTC', 'DSHUSD', 'DSHBTC']

        # Set up variables for receiver and main loop threads
        self._receiver_lock = threading.Lock()
        self._processor_lock = threading.Lock()
        self.receiver_q = queue.Queue()
        self.receiver_thread = None
        self.processing_thread = None

        self.ping_timer = None
        self.timeout = 5
        self._heartbeats = {}
        self._late_heartbeats = {}

        # Set up book-keeping variables & configurations
        self.api_version = None
        self.channels = {}  # Dict for matching channel ids with handlers
        self.channel_labels = {}  # Dict for matching channel ids with names
        self.channel_states = {}  # Dict for matching channel ids with status of each channel (alive/dead)
        self.channel_configs = {}  # Variables, as set by subscribe command
        self.wss_config = {}  # Config as passed by 'config' command

        self._event_handlers = {'error': self._raise_error,
                                'unsubscribed': self._handle_unsubscribed,
                                'subscribed': self._handle_subscribed,
                                'auth': self._handle_subscribed,
                                'unauth': self._handle_unsubscribed,
                                'info': self._handle_info,
                                'pong': self._handle_pong,
                                'conf': self._handle_conf}
        self._data_handlers = {'ticker': self._handle_ticker,
                               'book': self._handle_book,
                               'raw_book': self._handle_raw_book,
                               'candles': self._handle_candles,
                               'trades': self._handle_trades,
                               'auth': self._handle_auth}

        # 1XXXX == Error Code -> raise, 2XXXX == Info Code -> call
        def restart_client():
            self._controller_q.put('restart')

        self._code_handlers = {'20051': restart_client,
                               '20060': self.pause,
                               '20061': self.unpause,
                               '10000': InvalidEventError,
                               '10001': InvalidPairError,
                               '10300': GenericSubscriptionError,
                               '10301': AlreadySubscribedError,
                               '10302': InvalidChannelError,
                               '10400': GenericSubscriptionError,
                               '10401': NotSubscribedError,
                               '10011': InvalidBookPrecisionError,
                               '10012': InvalidBookLengthError}

    def eval_command(self, cmd):
        """
        Thread func to allow restarting / stopping of threads, for example
        when receiving a connection reset info message from the wss server.
        :return:
        """
        if cmd == 'restart':
            self.restart(soft=True)
        elif cmd == 'stop':
            self.stop()

    def _check_heartbeats(self, ts, *args, **kwargs):
        """
        Checks if the heartbeats are on-time. If not, the channel id is escalated
        to self._late_heartbeats and a warning is issued; once a hb is received
        again from this channel, it'll be removed from this dict, and an Info
        message logged.
        :param ts: timestamp, declares when data was received by the client
        :return:
        """
        for chan_id in self._heartbeats:
            if ts - self._heartbeats[chan_id] >= 10:
                if chan_id not in self._late_heartbeats:
                    try:
                        # This is newly late; escalate
                        log.warning("BitfinexWSS.heartbeats: Channel %s hasn't "
                                    "sent a heartbeat in %s seconds!",
                                    self.channel_labels[chan_id],
                                    ts - self._heartbeats[chan_id])
                        self._late_heartbeats[chan_id] = ts
                    except KeyError:
                        # This channel ID Is not known to us - log and raise
                        log.error("BitfinexWSS.heartbeats: Channel %s is not "
                                  "registered in the connector's registry! "
                                  "Restarting Connection to avoid errors..",
                                  chan_id)
                        raise UnknownChannelError
                else:
                    # We know of this already
                    continue
            else:
                # its not late
                try:
                    self._late_heartbeats.pop(chan_id)
                except KeyError:
                    # wasn't late before, check next channel
                    continue
                log.info("BitfinexWSS.heartbeats: Channel %s has sent a "
                         "heartbeat again!", self.channel_labels[chan_id])
            self.ping()

    def _check_ping(self):
        """
        Checks if the ping command timed out and raises TimeoutError if so.
        :return:
        """
        if time.time() - self.ping_timer > self.timeout:
            raise TimeoutError("Ping Command timed out!")

    def pause(self):
        """
        Pauses the client
        :return:
        """
        self._receiver_lock.acquire()
        log.info("BitfinexWSS.pause(): Pausing client..")

    def unpause(self):
        """
        Unpauses the client
        :return:
        """
        self._receiver_lock.release()
        log.info("BitfinexWSS.pause(): Unpausing client..")

    def start(self):
        """
        Start the websocket client threads
        :return:
        """
        super(BitfinexWSS, self).start()

        log.info("BitfinexWSS.start(): Initializing Websocket connection..")
        while self.conn is None:
            try:
                self.conn = create_connection(self.addr, timeout=10)
            except WebSocketTimeoutException:
                self.conn = None
                print("Couldn't create websocket connection - retrying!")

        log.info("BitfinexWSS.start(): Initializing receiver thread..")
        if not self.receiver_thread:
            self.receiver_thread = Thread(target=self.receive, name='Receiver Thread')
            self.receiver_thread.start()
        else:
            log.info("BitfinexWSS.start(): Thread not started! "
                     "self.receiver_thread is populated!")

        log.info("BitfinexWSS.start(): Initializing processing thread..")
        if not self.processing_thread:
            self.processing_thread = Thread(target=self.process, name='Processing Thread')
            self.processing_thread.start()
        else:
            log.info("BitfinexWSS.start(): Thread not started! "
                     "self.processing_thread is populated!")

        self.setup_subscriptions()

    def stop(self):
        """
        Stop all threads and modules of the client.
        :return:
        """
        super(BitfinexWSS, self).stop()

        log.info("BitfinexWSS.stop(): Stopping client..")

        log.info("BitfinexWSS.stop(): Joining receiver thread..")
        try:
            self.receiver_thread.join()
            if self.receiver_thread.is_alive():
                time.time(1)
        except AttributeError:
            log.debug("BitfinexWSS.stop(): Receiver thread was not running!")

        log.info("BitfinexWSS.stop(): Joining processing thread..")
        try:
            self.processing_thread.join()
            if self.processing_thread.is_alive():
                time.time(1)
        except AttributeError:
            log.debug("BitfinexWSS.stop(): Processing thread was not running!")

        log.info("BitfinexWSS.stop(): Closing websocket conection..")
        try:
            self.conn.close()
        except WebSocketConnectionClosedException:
            pass
        except AttributeError:
            # Connection is None
            pass

        self.conn = None
        self.processing_thread = None
        self.receiver_thread = None

        log.info("BitfinexWSS.stop(): Done!")

    def restart(self, soft=False):
        """
        Restarts client. If soft is True, the client attempts to re-subscribe
        to all channels which it was previously subscribed to.
        :return:
        """
        log.info("BitfinexWSS.restart(): Restarting client..")
        super(BitfinexWSS, self).restart()

        # cache channel labels temporarily if soft == True
        channel_labels = [self.channel_labels[k] for k in self.channel_labels] if soft else None

        # clear previous channel caches
        self.channels = {}
        self.channel_labels = {}
        self.channel_states = {}

        if channel_labels:
            # re-subscribe to channels
            for channel_name, kwargs in channel_labels:
                self._subscribe(channel_name, **kwargs)

    def receive(self):
        """
        Receives incoming websocket messages, and puts them on the Client queue
        for processing.
        :return:
        """
        while self.running:
            if self._receiver_lock.acquire(blocking=False):
                try:
                    raw = self.conn.recv()
                except WebSocketTimeoutException:
                    self._receiver_lock.release()
                    continue
                except WebSocketConnectionClosedException:
                    # this needs to restart the client, while keeping track
                    # of the currently subscribed channels!
                    self.conn = None
                    self._controller_q.put('restart')
                except AttributeError:
                    # self.conn is None, idle loop until shutdown of thread
                    self._receiver_lock.release()
                    continue
                msg = time.time(), json.loads(raw)
                log.debug("receiver Thread: Data Received: %s", msg)
                self.receiver_q.put(msg)
                self._receiver_lock.release()
            else:
                # The receiver_lock was locked, idling until available
                time.sleep(0.5)

    def process(self):
        """
        Processes the Client queue, and passes the data to the respective
        methods.
        :return:
        """

        while self.running:
            if self._processor_lock.acquire(blocking=False):

                if self.ping_timer:
                    try:
                        self._check_ping()
                    except TimeoutError:
                        log.exception("BitfinexWSS.ping(): TimedOut! (%ss)" %
                                      self.ping_timer)
                    except (WebSocketConnectionClosedException,
                            ConnectionResetError):
                        log.exception("BitfinexWSS.ping(): Connection Error!")
                        self.conn = None
                if not self.conn:
                    # The connection was killed - initiate restart
                    self._controller_q.put('restart')

                skip_processing = False

                try:
                    ts, data = self.receiver_q.get(timeout=0.1)
                except queue.Empty:
                    skip_processing = True
                    ts = time.time()
                    data = None

                if not skip_processing:
                    log.debug("Processing Data: %s", data)
                    if isinstance(data, list):
                        self.handle_data(ts, data)
                    else:  # Not a list, hence it could be a response
                        try:
                            self.handle_response(ts, data)
                        except UnknownEventError:

                            # We don't know what event this is- Raise an
                            # error & log data!
                            log.exception("main() - UnknownEventError: %s",
                                          data)
                            log.info("main() - Shutting Down due to "
                                     "Unknown Error!")
                            self._controller_q.put('stop')
                        except ConnectionResetError:
                            log.info("processor Thread: Connection Was reset, "
                                     "initiating restart")
                            self._controller_q.put('restart')

                self._check_heartbeats(ts)
                self._processor_lock.release()
            else:
                time.sleep(0.5)

    ##
    # Response Message Handlers
    ##

    def handle_response(self, ts, resp):
        """
        Passes a response message to the corresponding event handler, and also
        takes care of handling errors raised by the _raise_error handler.
        :param ts: timestamp, declares when data was received by the client
        :param resp: dict, containing info or error keys, among others
        :return:
        """
        log.info("handle_response: Handling response %s", resp)
        event = resp['event']
        try:
            self._event_handlers[event](ts, **resp)
        # Handle Non-Critical Errors
        except (InvalidChannelError, InvalidPairError, InvalidBookLengthError,
                InvalidBookPrecisionError) as e:
            log.exception(e)
            print(e)
        except (NotSubscribedError, AlreadySubscribedError) as e:
            log.exception(e)
            print(e)
        except GenericSubscriptionError as e:
            log.exception(e)
            print(e)

        # Handle Critical Errors
        except InvalidEventError as e:
            log.critical("handle_response(): %s; %s", e, resp)
            log.exception(e)
            raise SystemError(e)
        except KeyError:
            # unsupported event!
            raise UnknownEventError("handle_response(): %s" % resp)

    def _handle_subscribed(self, *args,  chanId=None, channel=None, **kwargs):
        """
        Handles responses to subscribe() commands - registers a channel id with
        the client and assigns a data handler to it.
        :param chanId: int, represent channel id as assigned by server
        :param channel: str, represents channel name
        """
        log.debug("_handle_subscribed: %s - %s - %s", chanId, channel, kwargs)
        if chanId in self.channels:
            raise AlreadyRegisteredError()

        self._heartbeats[chanId] = time.time()

        try:
            channel_key = ('raw_'+channel
                           if kwargs['prec'].startswith('R') and channel == 'book'
                           else channel)
        except KeyError:
            channel_key = channel

        try:
            self.channels[chanId] = self._data_handlers[channel_key]
        except KeyError:
            raise UnknownChannelError()

        # prep kwargs to be used as secondary value in dict key
        try:
            kwargs.pop('event')
        except KeyError:
            pass

        try:
            kwargs.pop('len')
        except KeyError:
            pass

        try:
            kwargs.pop('chanId')
        except KeyError:
            pass

        self.channel_labels[chanId] = (channel_key, kwargs)

    def _handle_unsubscribed(self, *args, chanId=None, **kwargs):
        """
        Handles responses to unsubscribe() commands - removes a channel id from
        the client.
        :param chanId: int, represent channel id as assigned by server
        """
        log.debug("_handle_unsubscribed: %s - %s", chanId, kwargs)
        try:
            self.channels.pop(chanId)
        except KeyError:
            raise NotRegisteredError()

        try:
            self._heartbeats.pop(chanId)
        except KeyError:
            pass

        try:
            self._late_heartbeats.pop(chanId)
        except KeyError:
            pass

    def _raise_error(self, *args, **kwargs):
        """
        Raises the proper exception for passed error code. These must then be
        handled by the layer calling _raise_error()
        """
        log.debug("_raise_error(): %s" % kwargs)
        try:
            error_code = str(kwargs['code'])
        except KeyError as e:
            raise FaultyPayloadError('_raise_error(): %s' % kwargs)

        try:
            raise self._code_handlers[error_code]()
        except KeyError:
            raise UnknownWSSError()

    def _handle_info(self, *args, **kwargs):
        """
        Handles info messages and executed corresponding code
        """
        if 'version' in kwargs:
            # set api version number and exit
            self.api_version = kwargs['version']
            print("Initialized API with version %s" % self.api_version)
            return
        try:
            info_code = str(kwargs['code'])
        except KeyError:
            raise FaultyPayloadError("_handle_info: %s" % kwargs)

        if not info_code.startswith('2'):
            raise ValueError("Info Code must start with 2! %s", kwargs)

        output_msg = "_handle_info(): %s" % kwargs
        log.info(output_msg)

        try:
            self._code_handlers[info_code]()
        except KeyError:
            raise UnknownWSSInfo(output_msg)

    def _handle_pong(self, ts, *args, **kwargs):
        """
        Handles pong messages; resets the self.ping_timer variable and logs
        info message.
        :param ts: timestamp, declares when data was received by the client
        :return:
        """
        log.info("BitfinexWSS.ping(): Ping received! (%ss)",
                 ts - self.ping_timer)
        self.ping_timer = None

    def _handle_conf(self, ts, *args, **kwargs):
        pass

    ##
    # Data Message Handlers
    ##

    def handle_data(self, ts, msg):
        """
        Passes msg to responding data handler, determined by its channel id,
        which is expected at index 0.
        :param ts: timestamp, declares when data was received by the client
        :param msg: list or dict of websocket data
        :return:
        """
        try:
            chan_id, *data = msg
        except ValueError as e:
            # Too many or too few values
            raise FaultyPayloadError("handle_data(): %s - %s" % (msg, e))
        self._heartbeats[chan_id] = ts
        if data[0] == 'hb':
            self._handle_hearbeat(ts, chan_id)
            return
        try:
            self.channels[chan_id](ts, chan_id, data)
        except KeyError:
            raise NotRegisteredError("handle_data: %s not registered - "
                                     "Payload: %s" % (chan_id, msg))

    @staticmethod
    def _handle_hearbeat(*args, **kwargs):
        """
        By default, does nothing.
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def _handle_ticker(self, ts, chan_id, data):
        """
        Adds received ticker data to self.tickers dict, filed under its channel
        id.
        :param ts: timestamp, declares when data was received by the client
        :param chan_id: int, channel id
        :param data: tuple or list of data received via wss
        :return:
        """
        pair = self.channel_labels[chan_id][1]['pair']
        entry = (*data, ts)
        self.data_q.put(('ticker', pair, entry))

    def _handle_book(self, ts, chan_id, data):
        """
        Updates the order book stored in self.books[chan_id]
        :param ts: timestamp, declares when data was received by the client
        :param chan_id: int, channel id
        :param data: dict, tuple or list of data received via wss
        :return:
        """
        pair = self.channel_labels[chan_id][1]['pair']
        entry = data, ts
        self.data_q.put(('order_book', pair, entry))

    def _handle_raw_book(self, ts, chan_id, data):
        """
        Updates the raw order books stored in self.raw_books[chan_id]
        :param ts: timestamp, declares when data was received by the client
        :param chan_id: int, channel id
        :param data: dict, tuple or list of data received via wss
        :return:
        """
        pair = self.channel_labels[chan_id][1]['pair']
        entry = data, ts
        self.data_q.put(('raw_order_book', pair, entry))

    def _handle_trades(self, ts, chan_id, data):
        """
        Files trades in self._trades[chan_id]
        :param ts: timestamp, declares when data was received by the client
        :param chan_id: int, channel id
        :param data: list of data received via wss
        :return:
        """
        pair = self.channel_labels[chan_id][1]['pair']
        entry = data, ts
        self.data_q.put(('trades', pair, entry))

    def _handle_candles(self, ts, chan_id, data):
        """
        Stores OHLC data received via wss in self.candles[chan_id]
        :param ts: timestamp, declares when data was received by the client
        :param chan_id: int, channel id
        :param data: list of data received via wss
        :return:
        """
        pair = self.channel_labels[chan_id][1]['key'].split(':')[-1][1:]
        entry = data, ts
        self.data_q.put(('ohlc', pair, entry))

    def _handle_auth(self, ts, chan_id, data):
        keys = {'hts': self._handle_auth_trades,
                'te': self._handle_auth_trades, 'tu': self._handle_auth_trades,
                'ps': self._handle_auth_positions,
                'pn': self._handle_auth_positions,
                'pu': self._handle_auth_positions,
                'pc': self._handle_auth_positions,
                'os': self._handle_auth_orders, 'on': self._handle_auth_orders,
                'ou': self._handle_auth_orders, 'oc': self._handle_auth_orders,
                'hos': self._handle_auth_orders, 'ws': self._handle_auth_wallet,
                'wu': self._handle_auth_wallet, 'bs': self._handle_auth_balance,
                'bu': self._handle_auth_balance,
                'mis': self._handle_auth_margin_info,
                'miu': self._handle_auth_margin_info,
                'fis': self._handle_auth_funding_info,
                'fiu': self._handle_auth_funding_info,
                'fos': self._handle_auth_offers, 'fon': self._handle_auth_offers,
                'fou': self._handle_auth_offers, 'foc': self._handle_auth_offers,
                'hfos': self._handle_auth_offers,
                'fcs': self._handle_auth_credits,
                'fcn': self._handle_auth_credits,
                'fcu': self._handle_auth_credits,
                'fcc': self._handle_auth_credits,
                'hfcs': self._handle_auth_credits,
                'fls': self._handle_auth_loans, 'fln': self._handle_auth_loans,
                'flu': self._handle_auth_loans, 'flc': self._handle_auth_loans,
                'hfls': self._handle_auth_loans,
                'hfts': self._handle_auth_funding_trades,
                'fte': self._handle_auth_funding_trades,
                'ftu': self._handle_auth_funding_trades}

        event, *_ = data

        try:
            keys[event](ts, data)
        except KeyError:
            log.exception('%s; %s', chan_id, data)
            raise UnknownEventError('The Passed event in data[0] is not '
                                    'associated with any data handler!')
        except Exception:
            log.exception("_handle_auth: %s - %s, %s", chan_id, event, data)
            raise

    def _handle_auth_trades(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_trades', 'NA', entry))

    def _handle_auth_positions(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_positions', 'NA', entry))

    def _handle_auth_orders(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_orders', 'NA', entry))

    def _handle_auth_wallet(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_wallet', 'NA', entry))

    def _handle_auth_balance(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_balance', 'NA', entry))

    def _handle_auth_margin_info(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_margin_info', 'NA', entry))

    def _handle_auth_funding_info(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_funding_info', 'NA', entry))

    def _handle_auth_offers(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_offers', 'NA', entry))

    def _handle_auth_credits(self, ts, data):
        entry = data, ts
        self.data_q.put(('account_credits', 'NA', entry))

    def _handle_auth_loans(self, event, data):
        entry = data, time.time()
        self.data_q.put(('account_loans', 'NA', entry))

    def _handle_auth_funding_trades(self, event, data):
        entry = data, time.time()
        self.data_q.put(('account_funding_trades', 'NA', entry))

    ##
    # Commands
    ##

    def send(self, payload):
        self.conn.send(json.dumps(payload))

    def ping(self):
        """
        Pings Websocket server to check if it's still alive.
        Required for connection tests
        :return:
        """
        self.ping_timer = time.time()
        self.send({'event': 'ping'})

    def setup_subscriptions(self):
        self.config(decimals_as_strings=True)
        for pair in self.pairs:
            self.ticker(pair)
            self.ohlc(pair)
            self.order_book(pair)
            self.raw_order_book(pair)
            self.trades(pair)

    def config(self, decimals_as_strings=True, ts_as_dates=False,
               sequencing=False, **kwargs):
        """
        Send configuration to websocket server
        :param decimals_as_strings: bool, turn on/off decimals as strings
        :param ts_as_dates: bool, decide to request timestamps as dates instead
        :param sequencing: bool, turn on sequencing
        :param kwargs:
        :return:
        """
        flags = 0
        if decimals_as_strings:
            flags += 8
        if ts_as_dates:
            flags += 32
        if sequencing:
            flags += 65536
        payload = {'event': 'conf', 'flags': flags}
        payload.update(kwargs)
        self.send(payload)

    def _subscribe(self, channel_name, **kwargs):
        if not self.conn:
            log.error("_subscribe(): Cannot subscribe to channel,"
                      "since the client has not been started!")
            return
        payload = {'event': 'subscribe', 'channel': channel_name}
        payload.update(**kwargs)
        log.debug("_subscribe: %s", payload)
        self.send(payload)

    def ticker(self, pair, **kwargs):
        """
        Subscribe to the passed pair's ticker channel.
        :param pair: str, Pair to request data for.
        :param kwargs:
        :return:
        """
        self._subscribe('ticker', symbol=pair, **kwargs)

    def order_book(self, pair, **kwargs):
        """
        Subscribe to the passed pair's order book channel.
        :param pair: str, Pair to request data for.
        :param kwargs:
        :return:
        """
        self._subscribe('book', symbol=pair, **kwargs)

    def raw_order_book(self, pair, prec=None, **kwargs):
        """
        Subscribe to the passed pair's raw order book channel.
        :param pair: str, Pair to request data for.
        :param kwargs:
        :return:
        """
        prec = 'R0' if prec is None else prec
        self._subscribe('book', pair=pair, prec=prec, **kwargs)

    def trades(self, pair, **kwargs):
        """
        Subscribe to the passed pair's trades channel.
        :param pair: str, Pair to request data for.
        :param kwargs:
        :return:
        """
        self._subscribe('trades', symbol=pair, **kwargs)

    def ohlc(self, pair, timeframe=None, **kwargs):
        """
        Subscribe to the passed pair's OHLC data channel.
        :param pair: str, Pair to request data for.
        :param timeframe: str, {1m, 5m, 15m, 30m, 1h, 3h, 6h, 12h,
                                1D, 7D, 14D, 1M}
        :param kwargs:
        :return:
        """
        valid_tfs = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D',
                     '7D', '14D', '1M']
        if timeframe:
            if timeframe not in valid_tfs:
                raise ValueError("timeframe must be any of %s" % valid_tfs)
        else:
            timeframe = '1m'
        pair = 't' + pair if not pair.startswith('t') else pair
        key = 'trade:' + timeframe + ':' + pair
        self._subscribe('candles', key=key, **kwargs)
