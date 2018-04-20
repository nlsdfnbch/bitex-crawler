"""Gate.io REST API backend.

Documentation available here:
    https://gateio.io/api2
"""
# Import Built-ins
import logging
import hashlib
import hmac
# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI
from bitex.exceptions import IncompleteCredentialsError

log = logging.getLogger(__name__)


def getsign(params, secret):
    """Caculate signature using params and secret."""
    bsecret = bytes(secret, encoding='utf8')

    sign = ''
    for key in params.keys():
        value = str(params[key])
        sign += key + '=' + value + '&'
    bsign = bytes(sign[:-1], encoding='utf8')

    mysign = hmac.new(bsecret, bsign, hashlib.sha512).hexdigest()
    return mysign


class GateioREST(RESTAPI):
    """Gateio REST API class."""

    def __init__(self, addr=None, user_id=None, key=None, secret=None, version=None, timeout=5,
                 config=None, proxies=None):
        """Initialize the class instance."""
        addr = addr or 'https:/'
        super(GateioREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                         timeout=timeout, config=config, proxies=proxies)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(GateioREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(GateioREST, self).sign_request_kwargs(endpoint, **kwargs)

        req_kwargs.pop('json')  # req_kwargs can not include json, or will 'Error: invalid data'
        # Parameters go into headers & data, so pop params key and generate signature
        params = req_kwargs.pop('params')

        # Update headers and data
        req_kwargs['headers'] = {
            "Content-type": "application/x-www-form-urlencoded",
            "KEY": self.key,
            "SIGN": getsign(params, self.secret)
        }
        # req_kwargs['data'] = params

        return req_kwargs
