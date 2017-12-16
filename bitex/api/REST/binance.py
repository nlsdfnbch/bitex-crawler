"""Bitfinex REST API backend.

Documentation available at:
    https://docs.bitfinex.com/docs
"""
# pylint: disable=too-many-arguments
# Import Built-ins
import logging
import json
import hashlib
import hmac
import time
import base64
import urllib
import urllib.parse

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class BinanceREST(RESTAPI):
    """Bitfinex REST API class."""

    def __init__(self, key=None, secret=None, version=None,
                 addr=None, timeout=None, config=None):
        """Initialize the class instance."""
        addr = 'https://api.binance.com/api'
        # We force version to None here as different endpoints require different versions,
        # so the interface will have to define the version as part of the endpoint.
        super(BinanceREST, self).__init__(addr=addr, version=None, key=key,
                                          secret=secret, timeout=timeout,
                                          config=config)

    def private_query(self, method_verb, endpoint, **request_kwargs):
        """
        Query a private API endpoint requiring signing of the request.

        :param method_verb: valid HTTP Verb (GET, PUT, DELETE, etc.)
        :param endpoint: str, API Endpoint
        :param request_kwargs: kwargs for request.Request()
        :return: request.Response() object
        """
        self.check_auth_requirements()
        request_kwargs = self.sign_request_kwargs(method_verb, endpoint, **request_kwargs)
        return self._query(method_verb, **request_kwargs)

    def sign_request_kwargs(self, method_verb, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(BinanceREST, self).sign_request_kwargs(endpoint,
                                                                   **kwargs)
        req_kwargs['params'] = {}
        # Prepare arguments for query request.
        try:
            params = kwargs.pop('params')
        except KeyError:
            params = {}

        params['timestamp'] = str(int(time.time()*1000))

        # Build request address
        req_string = urllib.parse.urlencode(params)

        # generate signature
        signature = hmac.new(self.secret.encode('utf-8'),
                             req_string.encode('utf-8'),
                             hashlib.sha256).hexdigest()

        req_string += '&signature=' + signature

        if method_verb == "GET" :
            req_kwargs['url'] += '?' + req_string
        else :
            req_kwargs['data'] = req_string

        req_kwargs['headers'] = {'X-MBX-APIKEY': self.key.encode('utf-8')}

        return req_kwargs


