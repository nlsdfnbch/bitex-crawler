"""BitHumb REST API backend.

Documentation available at:
    https://www.bithumb.com/u1/US127
"""

# Import Built-ins
import logging
import hashlib
import hmac
import base64
import urllib

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class BithumbREST(RESTAPI):
    """BitHumb REST API class."""

    def __init__(self, addr=None, key=None, secret=None, version=None, config=None, timeout=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = 'https://api.bithumb.com' if not addr else addr
        super(BithumbREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                          timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(BithumbREST, self).sign_request_kwargs(endpoint, **kwargs)

        # Parameters go into headers & data, so pop params key and generate signature
        params = req_kwargs.pop('params')
        # uri = self.generate_uri(endpoint)
        nonce = self.nonce()

        # uri_dict = {"endpoint": '/'+endpoint, "order_currency": "BTC", "payment_currency": "KRW"}
        uri_dict = dict({"endpoint": '/' + endpoint}, **params)
        str_data = urllib.parse.urlencode(uri_dict)
        message = '/' + endpoint + chr(0) + str_data + chr(0) + nonce
        sign = hmac.new(self.secret.encode("utf-8"), msg=message.encode("utf-8"),
                        digestmod=hashlib.sha512)
        signature = sign.hexdigest()
        signature = (base64.b64encode(signature.encode('utf-8'))).decode('utf-8')

        # Update headers and data
        req_kwargs['headers'] = {"Api-Key": self.key,
                                 "Api-Sign": signature,
                                 "Api-Nonce": nonce, }
        req_kwargs['data'] = uri_dict

        return req_kwargs
