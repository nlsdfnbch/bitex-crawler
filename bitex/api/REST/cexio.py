"""CEX.IO REST API backend.

Documentation available at:
    https://cex.io/cex-api
"""
# pylint: disable=too-many-arguments
# Import Built-ins
import logging
import hashlib
import hmac

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class CEXioREST(RESTAPI):
    """CEX.IO REST API class."""

    def __init__(self, addr=None, user_id=None, key=None, secret=None, version=None, config=None,
                 timeout=None, proxies=None):
        """Initialize the class instance."""
        addr = 'https://cex.io/api' if not addr else addr
        self.user_id = user_id
        super(CEXioREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                        timeout=timeout, config=config, proxies=proxies)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(CEXioREST, self).sign_request_kwargs(endpoint, **kwargs)

        # Parameters go into headers & data, so pop params key and generate signature
        nonce = self.nonce()
        message = nonce + self.user_id + self.key
        sign = hmac.new(self.secret.encode('utf8'), msg=message.encode("utf8"),
                        digestmod=hashlib.sha256)
        signature = sign.hexdigest()
        data = {
            "nonce": nonce,
            "key": self.key,
            "signature": signature,
            "content-type": "application/json"
        }
        req_kwargs['data'] = data

        return req_kwargs
