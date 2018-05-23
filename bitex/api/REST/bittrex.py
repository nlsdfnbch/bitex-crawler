"""Bittrex REST API backend.

Documentation available here:
    https://bittrex.com/home/api
"""
# Import Built-ins
import logging
import hashlib
import hmac
import urllib
import urllib.parse

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class BittrexREST(RESTAPI):
    """Bittrex REST API class."""

    def __init__(self, key=None, secret=None, version=None, addr=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        version = 'v1.1' if not version else version
        addr = 'https://bittrex.com/api' if not addr else addr
        super(BittrexREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                          timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request.

        Bittrex requires the request address to be included as a sha512 encoded
        string in the query header. This means that the request address used for
        signing, and the actual address used to send the request (incuding order
        of parameters) need to be identical. Hence, we must build the request
        address ourselves, instead of relying on the requests library to do it
        for us.
        """
        req_kwargs = super(BittrexREST, self).sign_request_kwargs(endpoint,
                                                                  **kwargs)
        req_kwargs['params'] = {}
        # Prepare arguments for query request.
        params = kwargs.pop('params', {})
        nonce = self.nonce()
        uri = self.generate_uri(endpoint)
        url = self.generate_url(uri)

        # Build request address
        req_string = '?apikey=' + self.key + "&nonce=" + nonce + '&'
        req_string += urllib.parse.urlencode(params)
        request_address = url + req_string
        req_kwargs['url'] = request_address

        # generate signature
        signature = hmac.new(self.secret.encode('utf-8'),
                             request_address.encode('utf-8'),
                             hashlib.sha512).hexdigest()
        req_kwargs['headers'] = {"apisign": signature}

        return req_kwargs
