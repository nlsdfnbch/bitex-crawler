"""CoinCheck REST API backend.

Documentation available here:
    https://coincheck.com/documents/exchange/api
"""
# Import Built-ins
import logging
import hashlib
import hmac
from urllib.parse import urlencode

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class CoincheckREST(RESTAPI):
    """CoinCheck REST API class."""

    def __init__(self, key=None, secret=None, version=None, addr=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = 'https://coincheck.com' if not addr else addr
        version = 'api' if not version else version
        super(CoincheckREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                            timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(CoincheckREST, self).sign_request_kwargs(endpoint,
                                                                    **kwargs)

        # Prepare argument for signature
        params = kwargs.pop('params', {})
        nonce = self.nonce()
        params = urlencode(params)

        # Create signature
        # sig = nonce + url + req

        data = (nonce + req_kwargs['url'] + '?' + params).encode('utf-8')
        hmac_sig = hmac.new(self.secret.encode('utf8'), data, hashlib.sha256)
        signature = hmac_sig.hexdigest()

        # Update headers
        req_kwargs['headers'] = {"ACCESS-KEY": self.key,
                                 "ACCESS-NONCE": nonce,
                                 "ACCESS-SIGNATURE": signature}

        return req_kwargs
