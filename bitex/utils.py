"""Supplies Decorators and utility functions."""
# Import Built-ins
import os
import configparser
import logging
from functools import wraps
from datetime import datetime

# Import Homebrew
from bitex.exceptions import UnsupportedEndpointError
from bitex.pairs import PairFormatter

log = logging.getLogger(__name__)


def check_version_compatibility(**version_func_pairs):
    """Check for correct version before method execution.

    Checks if the decorated function is compatible with the currently set API version.
    Should this not be the case, an UnsupportedEndpointError is raised.

    If the api version required contains '.', replace it with an
    underscore ('_') - the decorator will take care of it.
    """
    def decorator(func):
        """Decorate wrapper."""
        @wraps(func)
        def wrapped(*args, **kwargs):
            """Wrap function."""
            interface = args[0]
            for version, methods in version_func_pairs.items():
                if func.__name__ in methods:
                    if version.replace('_', '.') != interface.REST.version:
                        error_msg = ("Method not available on this API version"
                                     "(current is %s, supported is %s)" %
                                     (interface.REST.version,
                                      version.replace('_', '.')))
                        raise UnsupportedEndpointError(error_msg)

            return func(*args, **kwargs)
        return wrapped
    return decorator

# pylint: disable=protected-access


def check_and_format_pair(func):
    """Execute format_for() method if available, and assert that pair is supported by the exchange.

    When using this decorator, make sure that the first positional argument of
    the wrapped method is the pair, otherwise behaviour is undefined.
    """
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        """Wrap function."""
        pair, *remaining_args = args
        if isinstance(pair, str) and '_' in pair:
            pair = PairFormatter(pair.split('_')[0], pair.split('_')[1])
        try:
            if isinstance(pair, PairFormatter):
                pair = pair.format_for(self.name)
        except IndexError:
            pass
        if pair not in self.supported_pairs:
            print('self.supported_pairs',pair,self.supported_pairs,self)
            raise AssertionError("%s is not supported by this exchange!" % pair)
        return func(self, pair, *remaining_args, **kwargs)
    return wrapped


def load_configuration(fname):
    """Load the configuration file.

    Returns a configparser.ConfigParser() object.
    """
    if not os.path.exists(fname) or not os.path.isfile(fname):
        return None
    config = configparser.ConfigParser()
    config.read(fname)
    return config


# The following is a decorator which accepts a parameter, which should be a class that encapsulate
# a response and add useful methods, such as formatter.
def format_with(formatter):
    """Pass a class to be used as a wrapper in the innermost function."""
    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                response = function(*args, **kwargs)
            except NotImplementedError:
                log.error("Function %s has not been implemented yet!", function.__name__)
                raise

            if isinstance(response, list):
                return [formatter(function.__name__, r, *args, **kwargs) for r in response]

            try:
                return formatter(function.__name__, response, *args, **kwargs)
            except NotImplementedError:
                return response

        return wrapper

    return real_decorator


def timetrans(atime, tgttype):
    """Datetime format transform."""
    if isinstance(atime, str):
        if atime == 'now':
            dtdt = datetime.utcnow()
        elif '.' in atime:
            atime = atime.replace('Z', '')
            if 'T' in atime:
                dtdt = datetime.strptime(atime, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                dtdt = datetime.strptime(atime, '%Y-%m-%d %H:%M:%S.%f')
        else:
            if 'T' in atime:
                dtdt = datetime.strptime(atime, '%Y-%m-%dT%H:%M:%S')
            else:
                dtdt = datetime.strptime(atime, '%Y-%m-%d %H:%M:%S')
    elif isinstance(atime, datetime):
        dtdt = atime
    else:   # float timestamp
        dtdt = datetime.fromtimestamp(atime)

    if tgttype == 'str':
        ret = datetime.strftime(dtdt, '%Y-%m-%d %H:%M:%S')
    elif tgttype == 'datetime':
        ret = dtdt
    else:   # float timestamp
        ret = datetime.timestamp(dtdt)

    return ret
