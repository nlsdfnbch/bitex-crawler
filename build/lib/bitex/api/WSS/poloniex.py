# Import Built-Ins
import signal
import logging
import multiprocessing as mp
import time

# Import Third-Party
from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession
from asyncio import coroutine, get_event_loop
import requests

# Import Homebrew
from bitex.api.WSS.base import WSSAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class PoloniexSession(ApplicationSession):

    @coroutine
    def onJoin(self, *args, **kwargs):
        channel = self.config.extra['channel']

        def onTicker(*args, **kwargs):
            self.config.extra['queue'].put((channel, (args, kwargs, time.time())))

        if self.config.extra['is_killed'].is_set():
            raise KeyboardInterrupt()
        try:
            yield from self.subscribe(onTicker, self.config.extra['channel'])

        except Exception as e:
            raise


class PlnxEndpoint(mp.Process):
    def __init__(self, endpoint, q, **kwargs):
        super(PlnxEndpoint, self).__init__(name='%s Endpoint Process' %
                                                endpoint, **kwargs)
        self.endpoint = endpoint
        self.q = q
        self.is_killed = mp.Event()

    def run(self):
        self.runner = ApplicationRunner("wss://api.poloniex.com:443", 'realm1',
                                   extra={'channel': self.endpoint,
                                          'queue': self.q,
                                          'is_killed': self.is_killed})
        self.runner.run(PoloniexSession)

    def join(self, *args, **kwargs):
        self.is_killed.set()
        super(PlnxEndpoint, self).join(*args, **kwargs)


class PoloniexWSS(WSSAPI):
    def __init__(self, endpoints=None):
        super(PoloniexWSS, self).__init__(None, 'Poloniex')
        self.data_q = mp.Queue()
        self.connections = {}
        if endpoints:
            self.endpoints = endpoints
        else:
            r = requests.get('https://poloniex.com/public?command=returnTicker')
            self.endpoints = list(r.json().keys())
            self.endpoints.append('ticker')

        for endpoint in self.endpoints:
            self.connections[endpoint] = PlnxEndpoint(endpoint, self.data_q)

    def start(self):
        super(PoloniexWSS, self).start()
        for conn in self.connections:
            self.connections[conn].start()

    def stop(self):
        for conn in self.connections:
            self.connections[conn].join()
        super(PoloniexWSS, self).stop()


if __name__ == "__main__":

    wss = PoloniexWSS()
    wss.start()
    time.sleep(5)
    wss.stop()
    while not wss.data_q.empty():
        print(wss.data_q.get())