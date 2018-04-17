"""Basic REST API object."""
# Import Built-Ins
import logging
from os.path import join as join_path

# Import Third-Party
import requests

# Import Homebrew
from bitex.api.base import BaseAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class RESTAPI(BaseAPI):
    """
    Generic REST API interface.

    Supplies private and public query methods,
    as well as building blocks to customize the signature generation process.
    """

    def __init__(self, addr, timeout=None, key=None, secret=None, version=None,
                 config=None, proxies=None):
        """
        Initialize the RESTAPI instance.

        :param addr: str, API URL (excluding endpoint paths, if applicable)
        :param key: str, API key
        :param secret: str, API secret
        :param config: str, path to config file
        :param timeout: int or float, defines timeout for requests to API
        """
        super(RESTAPI, self).__init__(addr=addr, key=key, secret=secret,
                                      version=version, config=config, proxies=proxies)
        self.timeout = timeout if timeout else 10

    def generate_uri(self, endpoint):
        """
        Generate a Unique Resource Identifier (API Version + Endpoint).

        :param endpoint: str, endpoint path (i.e. /market/btcusd)
        :return: str, URI
        """
        return '/' + join_path(self.version or '', endpoint).replace('\\', '/')

    def generate_url(self, uri):
        """
        Generate a Unique Resource Locator (API Address + URI).

        :param uri: str, URI
        :return: str, URL
        """
        return self.addr + uri

    def sign_request_kwargs(self, endpoint, **kwargs):
        """
        Generate dummy Request Kwarg Signature.

        Extend this to implement signing of requests for private API calls. By default, it supplies
        a default URL using generate_uri and generate_url.

        :param endpoint: str, API Endpoint
        :param kwargs: Kwargs meant for requests.Request()
        :return: dict, request kwargs
        """
        uri = self.generate_uri(endpoint)
        url = self.generate_url(uri)
        template = {'url': url, 'headers': {}, 'files': {},
                    'data': {}, 'params': {}, 'auth': {}, 'cookies': {},
                    'hooks': {}, 'json': {}}
        template.update(kwargs)
        return template

    def _query(self, method_verb, **request_kwargs):
        """
        Send the request to the API via requests.

        :param method_verb: valid HTTP Verb (GET, PUT, DELETE, etc.)
        :param request_kwargs: kwargs for request.Request()
        :return: request.Response() object
        """
        # self.proxies = {"http": "http://127.0.0.1:1087", "https": "http://127.0.0.1:1087"}
        # print(method_verb,request_kwargs)
        if 'method' not in request_kwargs:
            resp = requests.request(method_verb, **request_kwargs, proxies=self.proxies,
                                    timeout=self.timeout)
        else:
            resp = requests.request(**request_kwargs, proxies=self.proxies, timeout=self.timeout)
        return resp

    def private_query(self, method_verb, endpoint, **request_kwargs):
        """
        Query a private API endpoint requiring signing of the request.

        :param method_verb: valid HTTP Verb (GET, PUT, DELETE, etc.)
        :param endpoint: str, API Endpoint
        :param request_kwargs: kwargs for request.Request()
        :return: request.Response() object
        """
        self.check_auth_requirements()
        request_kwargs['method'] = method_verb
        request_kwargs = self.sign_request_kwargs(endpoint, **request_kwargs)
        return self._query(method_verb, **request_kwargs)

    def public_query(self, method_verb, endpoint, **request_kwargs):
        """
        Query a public (i.e. unauthenticated) API endpoint and return the result.

        :param method_verb: valid HTTP Verb (GET, PUT, DELETE, etc.)
        :param endpoint: str, API Endpoint
        :param request_kwargs: kwargs for request.Request()
        :return: request.Response() object
        """
        request_kwargs['url'] = self.generate_url(self.generate_uri(endpoint))
        if 'endpointwithversion' in request_kwargs:
            if request_kwargs['endpointwithversion']:
                request_kwargs['url'] = endpoint
                del request_kwargs['endpointwithversion']
        return self._query(method_verb, **request_kwargs)
