# Import Built-Ins
import logging
from queue import Queue, Empty
from threading import Thread

# Import Third-Party

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


class WSSAPI:
    """
    Base Class with no actual connection functionality. This is added in the
    subclass, as the various wss APIs are too diverse in order to distill a
    sensible pool of common attributes.
    """
    def __init__(self, addr, name):
        """
        Initialize Object.
        :param addr:
        :param name:
        """
        log.debug("WSSAPI.__init__(): Initializing Websocket API")
        self.addr = addr
        self.name = name
        self.running = False

        # External Interface to interact with WSS.
        self.interface = Queue()

        # Internal Command Queue for restarts, stops and starts
        self._controller_q = Queue()

        # Queue storing all received data
        self.data_q = Queue()

        # Internal Controller thread, responsible for starts / restarts / stops
        self._controller_thread = None

    def start(self):
        """
        Starts threads. Extend this in your child class.
        :return:
        """
        log.info("WSSAPI.start(): Starting Basic Facilities")
        self.running = True
        if self._controller_thread is None or not self._controller_thread.is_alive():
            self._controller_thread = Thread(target=self._controller,
                                             daemon=True,
                                             name='%s Controller Thread' %
                                                  self.name)
            self._controller_thread.start()

    def stop(self):
        """
        Stops Threads. Overwrite this in your child class as necessary.
        :return:
        """
        log.debug("WSSAPI.stop(): Stopping..")
        self.running = False

    def restart(self):
        """
        Restart Threads.
        :return:
        """
        log.debug("WSSAPI.restart(): Restarting API Client..")
        self.stop()
        self.start()

    def _controller(self):
        """
        This method runs in a dedicated thread, calling self.eval_command().
        :return:
        """
        while self.running:
            try:
                cmd = self._controller_q.get(timeout=1)
            except (TimeoutError, Empty):
                continue
            log.debug("WSSAPI._controller(): Received command: %s", cmd)
            Thread(target=self.eval_command, args=(cmd,)).start()

    def send(self, payload):
        """
        Method to send instructions for subcribing, unsubscribing, etc to
        the exchange API.
        :return:
        """
        raise NotImplementedError()

    def eval_command(self, cmd):
        """
        Evaluates commands issued by internal threads. Extend this as necessary.
        :param cmd:
        :return:
        """
        if cmd == 'restart':
            self.restart()

        elif cmd == 'stop':
            self.stop()

        else:
            raise ValueError("Unknown Command passed to controller! %s" % cmd)

    def get(self, **kwargs):
        return self.data_q.get(**kwargs)
