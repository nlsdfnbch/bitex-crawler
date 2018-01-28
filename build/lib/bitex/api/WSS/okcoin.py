# Import Built-Ins
import logging
import json
import threading
import time

# Import Third-Party
from websocket import create_connection, WebSocketTimeoutException
import requests

# Import Homebrew
from bitex.api.WSS.base import WSSAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class OKCoinWSS(WSSAPI):
    def __init__(self):
        super(OKCoinWSS, self).__init__('wss://real.okcoin.com:10440/websocket/okcoinapi ',
                                        'OKCoin')
        self.conn = None

        self.pairs = ['BTC', 'LTC']
        self._data_thread = None

    def start(self):
        super(OKCoinWSS, self).start()

        self._data_thread = threading.Thread(target=self._process_data)
        self._data_thread.daemon = True
        self._data_thread.start()

    def stop(self):
        super(OKCoinWSS, self).stop()

        self._data_thread.join()

    def _process_data(self):
        self.conn = create_connection(self.addr, timeout=4)
        for pair in self.pairs:
            payload = [{'event': 'addChannel',
                        'channel': 'ok_sub_spotusd_%s_ticker' % pair},
                       {'event': 'addChannel',
                        'channel': 'ok_sub_spotusd_%s_depth_60' % pair},
                       {'event': 'addChannel',
                        'channel': 'ok_sub_spotusd_%s_trades' % pair},
                       {'event': 'addChannel',
                        'channel': 'ok_sub_spotusd_%s_kline_1min' % pair}]
            log.debug(payload)
            self.conn.send(json.dumps(payload))
        while self.running:
            try:
                data = json.loads(self.conn.recv())
            except (WebSocketTimeoutException, ConnectionResetError):
                self._controller_q.put('restart')

            if 'data' in data:
                pair = ''.join(data['channel'].split('spot')[1].split('_')[:2]).upper()
                self.data_q.put((data['channel'], pair, data['data'],
                                 time.time()))
            else:
                log.debug(data)
        self.conn = None