#import Built-Ins
import logging
from threading import Thread
from queue import Queue, Empty
import json
import time
import hmac
import hashlib
# Import Third-Party
from websocket import create_connection, WebSocketTimeoutException

# Import Homebrew
from bitex.api.WSS.base import WSSAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class HitBTCWSS(WSSAPI):
    def __init__(self, key=None, secret=None):
        data_addr = 'ws://api.hitbtc.com:80'
        super(HitBTCWSS, self).__init__(data_addr, 'HitBTC')
        self.trader_addr = 'ws://api.hitbtc.com:8080'

        self.data_thread = None
        self.supervisor_thread = None
        self.trade_thread = None

        self.key = key
        self.secret = secret

        self.trade_command_q = Queue()

    def start(self, duplex=False):
        super(HitBTCWSS, self).start()

        if duplex:
            self.trade_thread = Thread(target=self._trade_thread,
                                       name='Trader Thread')
            self.trade_thread.daemon = True
            self.trade_thread.start()

        self.data_thread = Thread(target=self._data_thread, name='Data Thread')
        self.data_thread.daemon = True
        self.data_thread.start()

    def stop(self):
        super(HitBTCWSS, self).stop()
        self.data_thread.join()
        if self.trade_thread:
            self.trade_thread.join()

    def eval_command(self, cmd):
        if cmd == 'restart_data':
            self.data_thread.join()
            self.data_thread = Thread(target=self._data_thread,
                                      name='Data Thread')
            self.data_thread.start()

    def _data_thread(self):
        try:
            conn = create_connection(self.addr)
        except Exception:
            self._controller_q.put('restart_data')
            return

        while self.running:
            try:
                data = conn.recv()
                data = json.loads(data)
            except WebSocketTimeoutException:
                self._controller_q.put('restart_data')
                return
            try:
                pair = data['MarketDataIncrementalRefresh']['symbol']
                endpoint = 'MarketDataIncrementalRefresh'
            except KeyError:
                pair = data['MarketDataSnapshotFullRefresh']['symbol']
                endpoint = 'MarketDataSnapshotFullRefresh'
            self.data_q.put((endpoint, pair, data[endpoint], time.time()))

    def _trade_thread(self):
        try:
            conn = create_connection(self.trader_addr)
        except Exception:
            log.exception('Trader Thread Error!')
            self._controller_q.put('restart_trader')
            return

        while self.running:
            try:
                data = conn.recv()
            except WebSocketTimeoutException:
                self._controller_q.put('restart_data')
                return
            self.data_q.put(json.loads(data))

            try:
                payload = self.trade_command_q.get()
            except Empty:
                continue

            try:
                conn.send(self.sign(payload))
            except (WebSocketTimeoutException, ConnectionResetError):
                continue

    def sign(self, payload):
        """
        Signature method which wraps signature and nonce parameters around a
        payload dictionary.
        :param payload:
        :return:
        """
        nonce = str(int(time.time() * 1000))
        package = {'apikey': self.key,
                   'message': {'nonce': nonce, 'payload': payload}}

        signature = hmac.new(self.secret, json.dumps(payload).hexdigest,
                             hashlib.sha512).hexdigest()
        package['signature'] = signature

        return json.dumps(package)

    def send(self, payload, auth=False):
        pkg = self.sign(payload) if auth else payload
        self.trade_command_q.put(pkg)
