"""Base class for interfaces."""
# Import Built-Ins
import logging
import abc

# Import Third-Party

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


class Interface(metaclass=abc.ABCMeta):
    """Base class for Interface objects."""

    def __init__(self, *, name, rest_api):
        """
        Initialize the Interface class instance.

        :param name: str, name of the Interface
        :param rest_api: REST API object.
        """
        self.REST = rest_api  # pylint: disable=invalid-name
        self.name = name
        try:
            self._supported_pairs = self._get_supported_pairs()
        except NotImplementedError:
            self._supported_pairs = None

    @property
    def supported_pairs(self):
        """
        Return a list of supported currncy pairs.

        :return: list
        """
        return self._supported_pairs

    @abc.abstractmethod
    def _get_supported_pairs(self):
        """
        Generate a list of supported pairs.

        Queries the API for a list of supported pairs and returns this as a
        list.

        Raises a NotImplementedError by default and needs to be overridden in
        child classes.

        :raises: NotImplementedError
        """
        raise NotImplementedError

    def is_supported(self, pair):
        """
        Check if the given pair is present in self._supported_pairs.

        Input can either be a string or a PairFormatter Obj (or child thereof).
        If it is the latter two, we'll call the format() method with the
        Interface's name attribute to acquire proper formatting.

        :param pair: Str, or bitex.pairs.PairFormatter Object
        :return: Bool
        """
        try:
            pair = pair.format_for(self.name)
        except AttributeError:
            pair = pair

        if pair in self.supported_pairs:
            return True
        return False

    def request(self, verb, endpoint, authenticate=False, **req_kwargs):
        """Query the API and return its result.

        :param verb: HTTP verb (GET, PUT, DELETE, etc)
        :param endpoint: Str
        :param authenticate: Bool, whether to call private_query or
                             public_query method.
        :param req_kwargs: Kwargs to pass to
                           _query / :class:`requests.Request()`
        :raise: UnsupportedPairError
        :return: :class:`requests.Response() Obj`
        """
        if authenticate:
            return self.REST.private_query(verb, endpoint, **req_kwargs)
        return self.REST.public_query(verb, endpoint, **req_kwargs)
