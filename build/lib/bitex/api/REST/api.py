"""
ABC for Exchange APIs
"""
# Import Built-Ins
import logging
import time
from abc import ABCMeta, abstractmethod

# Import Third-Party
import requests

# Import Homebrew
from bitex.api.REST.response import APIResponse

log = logging.getLogger(__name__)


class APIClient(metaclass=ABCMeta):
    """
    Base Class for API ojects. Provides basic methods to interact
    with exchange APIs, such as sending queries and signing messages to pass
    authentication.
    """

    def __init__(self, uri, api_version=None, key=None, secret=None, timeout=5):
        """
        Create API Client object.
        :param uri: string address for api (i.e. https://api.kraken.com/
        :param api_version: version, as required to query an endpoint
        :param key: API access key
        :param secret: API secret
        """
        self.key = key
        self.secret = secret
        self.uri = uri
        self.version = api_version if api_version else ''
        self.timeout = timeout
        log.debug("Initialized API Client for URI: %s; "
                  "Will request on API version: %s" %
                  (self.uri, self.version))

    def load_key(self, path):
        """
        Load key and secret from file.
        :param path: path to file with first two lines are key, secret respectively
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()

    def nonce(self):
        """
        Creates a Nonce value for signature generation
        :return:
        """
        return str(round(100000 * time.time()) * 2) 

    @staticmethod
    def api_request(*args, **kwargs):
        """
        Wrapper which converts a requests.Response into our custom APIResponse
        object
        :param args:
        :param kwargs:
        :return:
        """
        r = requests.request(*args, **kwargs)
        return APIResponse(r)

    @abstractmethod
    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        """
        Dummy Signature creation method. Override this in child.
        URL is required to be returned, as some Signatures use the url for
        sig generation, and api calls made must match the address exactly.
        param url: self.uri + self.version + endpoint (i.e https://api.kraken/0/Depth)
        param endpoint: api endpoint to call (i.e. 'Depth')
        param endpoint_path: self.version + endpoint (i.e. '0/Depth')
        param method_verb: valid request type (PUT, GET, POST etc)
        param return:
        """
        url = self.uri

        return url, {'params': {'test_param': "authenticated_chimichanga"}}

    def query(self, method_verb, endpoint, authenticate=False,
              *args, **kwargs):
        """
        Queries exchange using given data. Defaults to unauthenticated query.
        :param method_verb: valid request type (PUT, GET, POST etc)
        :param endpoint: endpoint path for the resource to query, sans the url &
                         API version (i.e. '/btcusd/ticker/').
        :param authenticate: Bool to determine whether or not a signature is
                             required.
        :param args: Optional args for requests.request()
        :param kwargs: Optional Kwargs for self.sign() and requests.request()
        :return: request.response() obj
        """
        if self.version:
            endpoint_path = '/' + self.version + '/' + endpoint
        else:
            endpoint_path = '/' + endpoint

        url = self.uri + endpoint_path
        if authenticate:  # sign off kwargs and url before sending request
            url, request_kwargs = self.sign(url, endpoint, endpoint_path,
                                            method_verb, *args, **kwargs)
        else:
            request_kwargs = kwargs
        log.debug("Making request to: %s, kwargs: %s", url, request_kwargs)
        r = self.api_request(method_verb, url, timeout=self.timeout,
                             **request_kwargs)
        log.debug("Made %s request made to %s, with headers %s and body %s. "
                  "Status code %s", r.request.method,
                  r.request.url, r.request.headers,
                  r.request.body, r.status_code)
        return r
