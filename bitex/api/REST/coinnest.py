"""Coinnest REST API backend.

Documentation available here:
    https://www.coinnest.co.kr/doc/intro.html
"""
# Import Built-ins
import logging
import hashlib
import hmac
import time
import urllib
# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class CoinnestREST(RESTAPI):
    """Coinnest REST API class."""

    def __init__(self, addr=None, key=None, secret=None, version=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = addr or 'https://api.coinnest.co.kr'
        super(CoinnestREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                           timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(CoinnestREST, self).sign_request_kwargs(endpoint, **kwargs)

        # Parameters go into headers & data, so pop params key and generate signature
        # params = req_kwargs.pop('params')

        nonce = str(int(round(time.time() * 1000)))
        payload = {"key": self.key, "nonce": nonce}
        str_data = urllib.parse.urlencode(payload)
        sign = str_data.encode('utf-8')

        md5 = hashlib.md5(self.secret.encode('utf-8')).hexdigest()
        key = md5.encode('utf-8')

        sign = hmac.new(key, sign, hashlib.sha256)
        signature = sign.hexdigest()

        data = {"key": self.key, "nonce": nonce, "signature": signature}

        # Update headers and data
        req_kwargs['data'] = data

        return req_kwargs
