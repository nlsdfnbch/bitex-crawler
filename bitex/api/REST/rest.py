"""
Contains all API Client sub-classes, which stores exchange specific details
and feature the respective exchanges and authentication method (sign()).
"""
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64
import time
import urllib
import urllib.parse

# Import Third-Party
from requests.auth import AuthBase

try:
    import pyjwt as jwt
    jwt = True
except ImportError:
    jwt = False

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class BitfinexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.bitfinex.com', timeout=5):
        super(BitfinexREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            req = kwargs['params']
        except KeyError:
            req = {}
        req['request'] = endpoint_path
        req['nonce'] = self.nonce()

        js = json.dumps(req)
        data = base64.standard_b64encode(js.encode('utf8'))

        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        headers = {"X-BFX-APIKEY": self.key,
                   "X-BFX-SIGNATURE": signature,
                   "X-BFX-PAYLOAD": data}

        return url, {'headers': headers}


class BitstampREST(APIClient):
    def __init__(self, user_id='', key=None, secret=None, api_version=None,
                 url='https://www.bitstamp.net/api', timeout=5):
        self.id = user_id
        super(BitstampREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def load_key(self, path):
        """
        Load key and secret from file.
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.id = f.readline().strip()

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        message = nonce + self.id + self.key

        signature = hmac.new(self.secret.encode(), message.encode(),
                             hashlib.sha256)
        signature = signature.hexdigest().upper()

        try:
            req = kwargs['params']
        except KeyError:
            req = {}
        req['key'] = self.key
        req['nonce'] = nonce
        req['signature'] = signature
        return url, {'data': req}


class BittrexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1.1',
                 url='https://bittrex.com/api', timeout=5):
        super(BittrexREST, self).__init__(url, api_version=api_version, key=key,
                                          secret=secret, timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):

        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        nonce = self.nonce()

        req_string = endpoint_path + '?apikey=' + self.key + "&nonce=" + nonce + '&'
        req_string += urllib.parse.urlencode(params)
        headers = {"apisign": hmac.new(self.secret.encode('utf-8'),
                                       (self.uri + req_string).encode('utf-8'),
                                       hashlib.sha512).hexdigest()}

        return self.uri + req_string, {'headers': headers, 'params': {}}


class CoincheckREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='api',
                 url='https://coincheck.com', timeout=5):
        super(CoincheckREST, self).__init__(url, api_version=api_version,
                                            key=key, secret=secret,
                                            timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):

        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        params = json.dumps(params)
        # sig = nonce + url + req
        data = (nonce + endpoint_path + params).encode('utf-8')
        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha256)
        signature = h.hexdigest()
        headers = {"ACCESS-KEY": self.key,
                   "ACCESS-NONCE": nonce,
                   "ACCESS-SIGNATURE": signature}

        return url, {'headers': headers}


class GdaxAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key.encode('utf-8')
        self.secret_key = secret_key.encode('utf-8')
        self.passphrase = passphrase.encode('utf-8')

    def __call__(self, request):
        timestamp = str(time.time())
        message = (timestamp + request.method + request.path_url +
                   (request.body.decode('utf-8') or ''))
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


class GDAXRest(APIClient):
    def __init__(self, passphrase='', key=None, secret=None, api_version=None,
                 url='https://api.gdax.com', timeout=5):
        self.passphrase = passphrase
        super(GDAXRest, self).__init__(url, api_version=api_version, key=key,
                                       secret=secret, timeout=timeout)

    def load_key(self, path):
        """
        Load key and secret from file.
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.passphrase = f.readline().strip()

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        auth = GdaxAuth(self.key, self.secret, self.passphrase)
        try:
            js = kwargs['params']
        except KeyError:
            js = {}

        return url, {'json': js, 'auth': auth}


class KrakenREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='0',
                 url='https://api.kraken.com', timeout=5):
        super(KrakenREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret, timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            req = kwargs['params']
        except KeyError:
            req = {}

        req['nonce'] = self.nonce()
        postdata = urllib.parse.urlencode(req)

        # Unicode-objects must be encoded before hashing
        encoded = (str(req['nonce']) + postdata).encode('utf-8')
        message = (endpoint_path.encode('utf-8') +
                   hashlib.sha256(encoded).digest())

        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        headers = {
            'API-Key': self.key,
            'API-Sign': sigdigest.decode('utf-8')
        }

        return url, {'data': req, 'headers': headers}


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


class OKCoinREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://www.okcoin.com/api', timeout=5):
        super(OKCoinREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret,
                                         timeout=timeout)

    def sign(self,url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()

        # sig = nonce + url + req
        data = (nonce + url).encode()

        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha256)
        signature = h.hexdigest()
        headers = {"ACCESS-KEY":       self.key,
                   "ACCESS-NONCE":     nonce,
                   "ACCESS-SIGNATURE": signature}

        return url, {'headers': headers}


class BTCERest(APIClient):
    def __init__(self, key=None, secret=None, api_version='3',
                 url='https://btc-e.com/api', timeout=5):
        super(BTCERest, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        post_params = params
        post_params.update({'nonce': nonce, 'method': endpoint.split('/', 1)[1]})
        post_params = urllib.parse.urlencode(post_params)

        signature = hmac.new(self.secret.encode('utf-8'),
                             post_params.encode('utf-8'), hashlib.sha512)
        headers = {'Key': self.key, 'Sign': signature.hexdigest(),
                   "Content-type": "application/x-www-form-urlencoded"}

        # split by tapi str to gain clean url;
        url = url.split('/tapi', 1)[0] + '/tapi'

        return url, {'headers': headers, 'params': params}


class CCEXRest(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://c-cex.com/t', timeout=5):
        super(CCEXRest, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        params['apikey'] = self.key
        params['nonce'] = nonce
        post_params = params
        post_params.update({'nonce': nonce, 'method': endpoint})
        post_params = urllib.parse.urlencode(post_params)

        url = uri + post_params

        sig = hmac.new(url, self.secret, hashlib.sha512)
        headers = {'apisign': sig}

        return url, {'headers': headers}


class CryptopiaREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://www.cryptopia.co.nz/api', timeout=5):
        super(CryptopiaREST, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        post_data = json.dumps(params)

        # generate signature
        md5 = hashlib.md5()
        md5.update(post_data.encode('utf-8'))
        request_content_b64_string = base64.b64encode(md5.digest()).decode('utf-8')
        signature = (self.key + 'POST' +
                     urllib.parse.quote_plus(uri).lower() +
                     nonce + request_content_b64_string)

        hmac_sig = base64.b64encode(hmac.new(base64.b64decode(self.secret),
                                             signature.encode('utf-8'),
                                             hashlib.sha256).digest())
        header_data = 'amx ' + self.key + ':' + hmac_sig.decode('utf-8') + ':' + nonce

        # Update req_kwargs keys
        headers = {'Authorization': header_data,
                                 'Content-Type': 'application/json; charset=utf-8'}

        return uri, {'headers': headers, 'data': post_data}


class GeminiREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.gemini.com', timeout=5):
        super(GeminiREST, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        payload = params
        payload['nonce'] = nonce
        payload['request'] = endpoint_path
        payload = base64.b64encode(json.dumps(payload))
        sig = hmac.new(self.secret, payload, hashlib.sha384).hexdigest()
        headers = {'X-GEMINI-APIKEY': self.key,
                   'X-GEMINI-PAYLOAD': payload,
                   'X-GEMINI-SIGNATURE': sig}
        return uri, {'headers': headers}


class YunbiREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v2',
                 url='https://yunbi.com/api', timeout=5):
        super(YunbiREST, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        params['tonce'] = nonce
        params['access_key'] = self.key
        post_params = urllib.parse.urlencode(params)
        msg = '%s|%s|%s' % (method_verb, endpoint_path, post_params)

        sig = hmac.new(self.secret, msg, hashlib.sha256).hexdigest()
        uri += post_params + '&signature=' + sig

        return uri, {}


class RockTradingREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.therocktrading.com', timeout=5):
        super(RockTradingREST, self).__init__(url, api_version=api_version,
                                              key=key, secret=secret,
                                              timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        payload = params
        payload['nonce'] = int(nonce)
        payload['request'] = endpoint_path

        msg = nonce + uri
        sig = hmac.new(self.secret.encode(), msg.encode(), hashlib.sha384).hexdigest()
        headers = {'X-TRT-APIKEY': self.key,
                   'X-TRT-Nonce': nonce,
                   'X-TRT-SIGNATURE': sig, 'Content-Type': 'application/json'}
        return uri, {'headers': headers}


class PoloniexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://poloniex.com', timeout=5):
        super(PoloniexREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        params['nonce'] = self.nonce()
        payload = params

        msg = urllib.parse.urlencode(payload).encode('utf-8')
        sig = hmac.new(self.secret.encode('utf-8'), msg, hashlib.sha512).hexdigest()
        headers = {'Key': self.key, 'Sign': sig}
        return uri, {'headers': headers, 'data': params}


class QuoineREST(APIClient):
    """
    The Quoine Api requires the API version to be designated in each requests's
    header as {'X-Quoine-API-Version': 2}
    """
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://api.quoine.com/', timeout=5):
        if not jwt:
            raise SystemError("No JWT Installed! Quoine API Unavailable!")
        super(QuoineREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        path = endpoint_path + urllib.parse.urlencode(params)
        msg = {'path': path, 'nonce': self.nonce(), 'token_id': self.key}

        signature = jwt.encode(msg, self.secret, algorithm='HS256')
        headers = {'X-Quoine-API-Version': '2', 'X-Quoine-Auth': signature,
                   'Content-Type': 'application/json'}
        return self.uri+path, {'headers': headers}


class QuadrigaCXREST(APIClient):
    def __init__(self, key=None, secret=None, client_id='', api_version='v2',
                 url='https://api.quoine.com/', timeout=5):
        self.client_id = client_id
        super(QuadrigaCXREST, self).__init__(url, api_version=api_version,
                                             key=key, secret=secret,
                                             timeout=timeout)

    def load_key(self, path):
        """
        Load key and secret from file.
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.client_id = f.readline().strip()

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        msg = nonce + self.client_id + self.key

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha256)
        headers = {'key': self.key, 'signature': signature,
                   'nonce': nonce}
        return self.uri, {'headers': headers, 'data': params}


class HitBTCREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='1',
                 url='http://api.hitbtc.com/api/', timeout=5):
        api_version = '' if not api_version else api_version
        super(HitBTCREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret,
                                         timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        kwargs['nonce'] = nonce
        kwargs['apikey'] = self.key
        msg = endpoint_path + urllib.parse.urlencode(params)

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha512)
        headers = {'Api-signature': signature}
        return self.uri + msg, {'headers': headers, 'data': params}


class VaultoroREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://api.vaultoro.com', timeout=5):
        api_version = '' if not api_version else api_version
        super(VaultoroREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        kwargs['nonce'] = nonce
        kwargs['apikey'] = self.key
        msg = uri + urllib.parse.urlencode(params)

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-Signature': signature}
        return msg, {'headers': headers}


class BterREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='http://data.bter.com/api', timeout=5):
        api_version = '1' if not api_version else api_version
        super(BterREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        kwargs['nonce'] = nonce

        msg = urllib.parse.urlencode(params)

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha512).hexdigest()
        headers = {'Key': signature, 'Sign': signature}
        return uri + msg, {'headers': headers}

