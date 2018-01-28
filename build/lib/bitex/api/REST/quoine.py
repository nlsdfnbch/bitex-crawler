"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import urllib
import urllib.parse

try:
    import jwt
    jwt_available = True
except ImportError:
    jwt_available = False

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class QuoineREST(APIClient):
    """
    The Quoine Api requires the API version to be designated in each requests's
    header as {'X-Quoine-API-Version': 2}
    """
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://api.quoine.com', timeout=5):
        if not jwt_available:
            raise SystemError("No JWT Installed! Quoine API Unavailable!")
        super(QuoineREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        if method_verb != 'POST':
            endpoint_path += urllib.parse.urlencode(params)
        msg = {'path': endpoint_path, 'nonce': self.nonce(), 'token_id': self.key}

        signature = jwt.encode(msg, self.secret, algorithm='HS256')
        headers = {'X-Quoine-API-Version': '2', 'X-Quoine-Auth': signature,
                   'Content-Type': 'application/json'}
        request = {'headers': headers}
        if method_verb == 'POST':
            request['json'] = params
        return self.uri + endpoint_path, request

