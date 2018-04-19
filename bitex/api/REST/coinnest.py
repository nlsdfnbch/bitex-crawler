"""Coinnest REST API backend.

Documentation available here:
    https://www.coinnest.co.kr/doc/intro.html
"""
# Import Built-ins
import logging
import hashlib
import hmac
import warnings
import time
import urllib
# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI
from bitex.exceptions import IncompleteCredentialsError
from bitex.exceptions import IncompleteCredentialConfigurationWarning

log = logging.getLogger(__name__)


class CoinnestREST(RESTAPI):
    """Coinnest REST API class."""

    def __init__(self, addr=None, user_id=None, key=None, secret=None, version=None, timeout=5,
                 config=None, proxies=None):
        """Initialize the class instance."""
        addr = addr or 'https://api.coinnest.co.kr'
        super(CoinnestREST, self).__init__(addr=addr, version=version,
                                           key=key, secret=secret,
                                           timeout=timeout, config=config, proxies=proxies)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(CoinnestREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(CoinnestREST, self).sign_request_kwargs(endpoint, **kwargs)

        # Parameters go into headers & data, so pop params key and generate signature
        # params = req_kwargs.pop('params')

        nonce = str(int(round(time.time() * 1000)))
        uri_array = {"key": self.key, "nonce": nonce}
        str_data = urllib.parse.urlencode(uri_array)
        sign = bytes(str_data, encoding='utf8')

        md5 = hashlib.md5(bytes(self.secret, encoding='utf8')).hexdigest()
        key = bytes(md5, encoding='utf8')

        sign = hmac.new(key, sign, hashlib.sha256)
        signature = sign.hexdigest()

        data = {"key": self.key, "nonce": nonce, "signature": signature}

        # Update headers and data
        req_kwargs['data'] = data

        return req_kwargs
