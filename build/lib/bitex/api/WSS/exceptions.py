"""
Contains Exceptions (Errors, Warnings, Infos) relevant to BtfxWSS.

Generally, BtfxServerInfo & BtfxServerError Exceptions should
be handled.

BtfxClientErrors should be raised.

"""
# Import Built-Ins
import logging

# Init Logging Facilities
log = logging.getLogger(__name__)
server_log = logging.getLogger('BitfinexServer')
client_log = logging.getLogger('BitfinexClient')


class BtfxServerInfo(Exception):
    """
    General Info exception for status codes sent by the BTFX server
    (field 'code' in payload and 'event' == 'info').
    """
    def __init__(self, message=None):
        if not message:
            message = "BTFX Generic Server Info - Error Code not provided"
        super(BtfxServerInfo, self).__init__(message)


class RestartServiceInfo(BtfxServerInfo):
    """
    The server has issued us to restart / reconnect to the websocket service.
    """
    def __init__(self, message=None):
        if not message:
            message = 'Code 20051: Please reconnect / restart your client!'
        super(RestartServiceInfo, self).__init__(message)


class PauseWSSClientInfo(BtfxServerInfo):
    """
    The Server has issued a pause on activity, due to the trading engine being
    refreshed (according to docs@12.01.18, this takes around 10s).
    """
    def __init__(self, message=None):
        if not message:
            message = 'Code 20060: Refreshing Trading Engine - Please pause any activity!'
        super(PauseWSSClientInfo, self).__init__(message)


class UnpauseWSSClientInfo(BtfxServerInfo):
    """
    The Server has given greenlight to continue activity.
    """
    def __init__(self, message=None):
        if not message:
            message = 'Code 20051: Trading engine refreshed - Continue activity'
        super(UnpauseWSSClientInfo, self).__init__(message)


class BtfxServerError(Exception):
    """
    General Error for any status codes sent by bitfinex websockets
    ('event' field of value 'info' or 'error').

    These should be handled and activity should continue as normal.
    """
    def __init__(self, message=None):
        if not message:
            message = "BTFX Generic Server Error - Error Code not provided!"
        super(BtfxServerError, self).__init__(message)


class GenericSubscriptionError(BtfxServerError):
    """
    A generic Error occurred during the subscription process - check your
    payload and consult with BTFX support.
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10300/10400: Generic Subscription Error!"
        server_log.error(message)
        super(GenericSubscriptionError, self).__init__(message)


class AlreadySubscribedError(BtfxServerError):
    """
    The subscription existed already.
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10301: Subscription Error - Already Subscribed!"
        server_log.error(message)
        super(AlreadySubscribedError, self).__init__(message)


class NotSubscribedError(BtfxServerError):
    """
    You were not subscribed to the channel you've tried unsubscribing from.
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10401: Subscription Error - Not Subscribed!"
        server_log.error(message)
        super(NotSubscribedError, self).__init__(message)


class InvalidEventError(BtfxServerError):
    """
    Raised when an unknown event is sent via the websocket ('event' field in
    payload).
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10000: Event Error - Unknown Event Passed!"
        server_log.error(message)
        super(InvalidEventError, self).__init__(message)


class InvalidPairError(BtfxServerError):
    """
    Raised when an unknown pair error code is sent via the websocket.
    (field 'code' in payload)
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10001: Pair Error - Unknown Pair Passed!"
        server_log.error(message)
        super(InvalidPairError, self).__init__(message)


class InvalidChannelError(BtfxServerError):
    """
    Raised when an unknown channel error code is sent via the websocket.
    (field 'code' in payload, 'event' == 'error')
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10302: Channel Error - Unknown Channel Passed!"
        server_log.error(message)
        super(InvalidChannelError, self).__init__(message)


class InvalidBookPrecisionError(BtfxServerError):
    """
    Raised when subscribing to the book channel and passing an invalid
    book precision parameter.
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10011: Book Precision Error - Unknown Book Precision Passed!"
        server_log.error(message)
        super(InvalidBookPrecisionError, self).__init__(message)


class InvalidBookLengthError(BtfxServerError):
    """
    Raised when subscribing to the book channel and passing an invalid
    book length parameter.
    """
    def __init__(self, message=None):
        if not message:
            message = "Code 10012: Book Length Error - Unknown Book Length Passed!"
        server_log.error(message)
        super(InvalidBookLengthError, self).__init__(message)


class BtfxClientError(Exception):
    """
    General class for BtfxWSS Client-related errors. This includes errors raised due
    to unknown events, status codes, and book-keeping errors (i.e. duplicate
    subscriptions and the like).

    These should be raised, as they indicate an error in code and function,
    possibly leading to faulty data.
    """
    def __init__(self, message=None):
        if not message:
            message = "BTFX Generic Client Error - Error Code not provided!"
        super(BtfxClientError, self).__init__(message)


class UnknownEventError(BtfxClientError):
    """
    Raised when an unknown event is received via the websocket ('event' field in
    payload).
    """
    def __init__(self, message=None):
        if not message:
            message = "Client Error: Received an unsupported event!"
        client_log.error(message)
        super(BtfxClientError, self).__init__(message)


class UnknownWSSError(BtfxClientError):
    """
    Raised when an unknown error code is received via the websocket.
    (field 'code' in payload, 'event' == 'error')
    """
    def __init__(self, message=None):
        if not message:
            message = "Client Error: Received an unknown error!"
        client_log.error(message)
        super(UnknownWSSError, self).__init__(message)


class UnknownChannelError(BtfxClientError):
    """
    Raised when a channel is received via the websocket for which BtfxWSS has
    no data handler set in _data_handlers.
    (field 'channel' in payload, 'event' == 'subscribed' | 'unsubscribed')
    """
    def __init__(self, message=None):
        if not message:
            message = "Client Error: Received an unknown channel!"
        client_log.error(message)
        super(UnknownChannelError, self).__init__(message)


class UnknownWSSInfo(BtfxClientError):
    """
    Raised when an unknown info code is received via the websocket.
    (field 'code' in payload, 'event' == 'info')
    """
    def __init__(self, message=None):
        if not message:
            message = "Client Error: Received an unknown info code!"
        client_log.error(message)
        super(UnknownWSSInfo, self).__init__(message)


class AlreadyRegisteredError(BtfxClientError):
    """
    Raised when a subscription response is received, but the channel ID has
    already been registered in BtfxWSS.channels attribute;
    """
    def __init__(self, message=None):
        if not message:
            message = "Client Error: Received Registration command for " \
                      "a channel that is already subscribed - " \
                      "it has been overwritten!"
        client_log.error(message)
        super(AlreadyRegisteredError, self).__init__(message)


class NotRegisteredError(BtfxClientError):
    """
    Raised when data is received, but its channel ID has not been registered
    with the client, or the user tries unsubscribing from a channel that is
    not regustered with the client.
    """
    def __init__(self, message=None):
        if not message:
            message = "Client Error: Received data for a channel which has not" \
                      "been registered with the client!"
        client_log.error(message)
        super(NotRegisteredError, self).__init__(message)


class FaultyPayloadError(BtfxClientError):
    """
    Raised when a payload has been passed to an incorrect method, or the payload
    does not contain the fields, or is not formmatted as expected.
    """
    def __init__(self, message):
        client_log.error(message)
        super(FaultyPayloadError, self).__init__(message)