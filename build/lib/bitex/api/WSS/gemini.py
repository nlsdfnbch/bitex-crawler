# Import Built-Ins
import logging
import time
from threading import Thread
from queue import Queue

# Import Third-Party
import requests

# Import Homebrew
from bitex.api.WSS.base import WSSAPI

# Init Logging Facilities
log = logging.getLogger(__name__)

from websocket import create_connection, WebSocketTimeoutException


class GeminiWSS(WSSAPI):
    def __init__(self, endpoints=None):
        super(GeminiWSS, self).__init__('wss://api.gemini.com/v1/', 'Gemini')
        self.endpoints = (endpoints if endpoints else
                          requests.get('https://api.gemini.com/v1/symbols').json())
        self.endpoints = ['marketdata/' + x.upper() for x in self.endpoints]
        self.endpoint_threads = {}
        self.threads_running = {}
        self.restarter_thread = None
        self.restart_q = Queue()

    def _restart_thread(self):
        """
        Restarts subscription threads if their connection drops.
        :return:
        """
        while self.running['restart_thread']:
            try:
                endpoint = self.restart_q.get(timeout=.5)
            except TimeoutError:
                continue
            log.info("_restart_thread(): Restarting Thread for endpoint %s",
                     endpoint)
            self.unsubscribe(endpoint)
            self.subscribe(endpoint)

    def _subscription_thread(self, endpoint):
        """
        Thread Method, running the connection for each endpoint.
        :param endpoint:
        :return:
        """
        try:
            conn = create_connection(self.addr + endpoint, timeout=5)
        except WebSocketTimeoutException:
            self.restart_q.put(endpoint)
            return

        while self.threads_running[endpoint]:
            try:
                msg = conn.recv()
            except WebSocketTimeoutException:
                self._controller_q.put(endpoint)

            log.debug("%s, %s", endpoint, msg)
            ep, pair = endpoint.split('/')
            log.debug("_subscription_thread(): Putting data on q..")
            try:
                self.data_q.put((ep, pair, msg, time.time()), timeout=1)
            except TimeoutError:
                continue
            finally:
                log.debug("_subscription_thread(): Data Processed, looping back..")
        conn.close()
        log.debug("_subscription_thread(): Thread Loop Ended.")

    def start(self):
        super(GeminiWSS, self).start()

        log.debug("GeminiWSS.start(): launching Endpoint Threads..")
        for endpoint in self.endpoints:
            self.subscribe(endpoint)

    def stop(self):
        super(GeminiWSS, self).stop()
        log.debug('stop(): Shutting down Endpoint threads..')
        for endpoint in self.endpoints:
            try:
                self.unsubscribe(endpoint)
            except KeyError:
                pass
        while not all(not self.endpoint_threads[x].is_alive() for x in self.endpoint_threads):
            time.sleep(1)
            log.debug('stop(): Waiting for threads to shutdown..')
        log.debug("stop(): Shutting down complete - running Grabage Collector..")
        self.garbage_collector()

    def restart(self):
        self.stop()
        self.start()

    def subscribe(self, endpoint):
        log.debug("GeminiWSS.subscribe(): Starting Thread for endpoint %s",
                  endpoint)
        self.threads_running[endpoint] = True
        t = Thread(target=self._subscription_thread,
                   args=(endpoint,), name=endpoint)
        t.daemon = True
        t.start()
        self.endpoint_threads[endpoint] = t

    def unsubscribe(self, endpoint):
        self.threads_running[endpoint] = False
        try:
            self.endpoint_threads[endpoint].join(timeout=1)
        except TimeoutError:
            self.endpoint_threads.pop(endpoint)

        self.garbage_collector()

    def garbage_collector(self):
        for endpoint in self.endpoints:
            try:
                if self.endpoint_threads[endpoint].is_alive():
                    continue
                else:
                    self.endpoint_threads.pop(endpoint)
            except KeyError:
                pass

    def eval_command(self, cmd):
        if cmd in self.endpoints:
            self.subscribe(cmd)
        elif cmd == 'stop':
            self.stop()



