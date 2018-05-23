"""Cryptopia REST API backend.

Documentation available here:
    https://www.cryptopia.co.nz/Forum/Thread/255
    https://www.cryptopia.co.nz/Forum/Thread/256
"""
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64
import urllib
import urllib.parse
import io

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


def decode_base64(data):
    """Decode base64， padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'=' * missing_padding
    return base64.decodebytes(data)


class CryptopiaREST(RESTAPI):
    """Cryptopia REST API class."""

    def __init__(self, key=None, secret=None, version=None, config=None, addr=None, timeout=5,
                 **kwargs):
        """Initialize the class instance."""
        addr = 'https://www.cryptopia.co.nz/api' if not addr else addr
        super(CryptopiaREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                            timeout=timeout, config=config, **kwargs)

    def _query(self, method_verb, **request_kwargs):
        """Query the Cryptopia REST API.

        For whatever reason, Cryptopia Sends a BOM Header. This is a 3 Byte
        header, which prevents requests.Request.json() to properly decode
        the response's content. We thus remove the first 3 bytes if Response.json()
        fails.
        """
        resp = super(CryptopiaREST, self)._query(method_verb, **request_kwargs)
        try:
            resp.json()
        except json.JSONDecodeError:

            bom_str = io.BytesIO(resp._content)
            bom_str.read(3)
            bom_removed_str = bom_str.read(len(resp._content))
            try:
                json.loads(bom_removed_str.decode('utf-8'))
            except json.JSONDecodeError:
                return resp

            resp._content = bom_removed_str
        return resp

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(CryptopiaREST, self).sign_request_kwargs(endpoint,
                                                                    **kwargs)

        # Prepare POST Payload arguments
        nonce = self.nonce()
        params = req_kwargs.pop('params', {})
        post_data = json.dumps(params)
        url = 'https://www.cryptopia.co.nz/Api/' + endpoint
        parsed_url = urllib.parse.quote_plus(url).lower()

        # generate signature
        md5 = hashlib.md5()
        md5.update(post_data.encode('utf-8'))
        request_content_b64_string = base64.b64encode(md5.digest()).decode('utf-8')
        signature = (self.key + 'POST' + parsed_url + nonce + request_content_b64_string)

        sec = decode_base64(self.secret.encode('utf-8'))
        hmac_sig = base64.b64encode(hmac.new(sec,
                                             signature.encode('utf-8'),
                                             hashlib.sha256).digest())
        header_data = 'amx ' + self.key + ':' + hmac_sig.decode('utf-8') + ':' + nonce

        # Update req_kwargs keys
        req_kwargs['url'] = url
        req_kwargs['headers'] = {'Authorization': header_data,
                                 'Content-Type': 'application/json; charset=utf-8'}
        req_kwargs['data'] = post_data

        return req_kwargs
