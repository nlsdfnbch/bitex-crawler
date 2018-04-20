"""Exmo REST API backend.

Documentation available here:
    https://exmo.com/en/api
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
from bitex.exceptions import IncompleteCredentialsError

log = logging.getLogger(__name__)


class ExmoREST(RESTAPI):
    """Exmo REST API class."""

    def __init__(self, addr=None, user_id=None, key=None, secret=None, version=None, timeout=5,
                 config=None, proxies=None):
        """Initialize the class instance."""
        addr = addr or 'https://api.exmo.com'
        super(ExmoREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                       timeout=timeout, config=config, proxies=proxies)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(ExmoREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(ExmoREST, self).sign_request_kwargs(endpoint, **kwargs)

        # Parameters go into headers & data, so pop params key and generate signature
        params = req_kwargs.pop('params')
        params['nonce'] = int(round(time.time() * 1000))
        params = urllib.parse.urlencode(params)

        sign = hmac.new(key=bytes(self.secret, encoding='utf8'), digestmod=hashlib.sha512)
        sign.update(params.encode('utf-8'))
        signature = sign.hexdigest()

        # Update headers and data
        req_kwargs['headers'] = {"Content-type": "application/x-www-form-urlencoded",
                                 "Key": self.key,
                                 "Sign": signature, }
        req_kwargs['data'] = params

        return req_kwargs
