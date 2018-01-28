"""
Provides utility functions used across more than one module or sub module.

"""

# Import Built-Ins
import logging
import json
from functools import wraps

# Import Third-Party
import requests

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


def return_api_response(formatter=None):
    """
    Decorator, which Applies the referenced formatter (if available) to the
    function output and adds it to the APIResponse Object's `formatted`
    attribute.
    :param formatter: bitex.formatters.Formatter() obj
    :return: bitex.api.response.APIResponse()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                r = func(*args, **kwargs)
            except Exception:
                log.exception("return_api_response(): Error during call to %s(%s, %s)",
                              func.__name__, args, kwargs)
                raise

            # Check Status
            try:
                r.raise_for_status()
            except requests.HTTPError:
                log.exception("return_api_response: HTTPError for url %s",
                              r.request.url)

            #  Verify json data
            try:
                data = r.json()
            except json.JSONDecodeError:
                log.error('return_api_response: Error while parsing json. '
                          'Request url was: %s, result is: '
                          '%s', r.request.url, r.text)
                data = None
            except Exception:
                log.exception("return_api_response(): Unexpected error while parsing "
                              "json from %s", r.request.url)
                raise

            # Format, if available
            if formatter is not None and data:
                try:
                    r.formatted = formatter(data, *args, **kwargs)
                except Exception:
                    log.exception("Error while applying formatter!")

            return r

        return wrapper
    return decorator
