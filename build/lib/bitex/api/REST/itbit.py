"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class ItbitREST(APIClient):
    def __init__(self, user_id = '', key=None, secret=None, api_version='v1',
                 url='https://api.itbit.com', timeout=5):
        self.userId = user_id
        super(ItbitREST, self).__init__(url, api_version=api_version,
                                 key=key, secret=secret, timeout=timeout)

    def load_key(self, path):
        """
        Load user id, key and secret from file.
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.userId = f.readline().strip()

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        verb = method_verb

        if verb in ('PUT', 'POST'):
            body = params
        else:
            body = {}

        timestamp = self.nonce()
        nonce = self.nonce()

        message = json.dumps([verb, url, body, nonce, timestamp],
                             separators=(',', ':'))
        sha256_hash = hashlib.sha256()
        nonced_message = nonce + message
        sha256_hash.update(nonced_message.encode('utf8'))
        hash_digest = sha256_hash.digest()
        hmac_digest = hmac.new(self.secret.encode('utf-8'),
                               url.encode('utf-8') + hash_digest,
                               hashlib.sha512).digest()
        signature = base64.b64encode(hmac_digest)

        auth_headers = {
            'Authorization': self.key + ':' + signature.decode('utf8'),
            'X-Auth-Timestamp': timestamp,
            'X-Auth-Nonce': nonce,
            'Content-Type': 'application/json'
        }
        return url, {'headers': auth_headers}

