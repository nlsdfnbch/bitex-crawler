# Import Third-Party
from requests import Response


class APIResponse(Response):

    def __init__(self, req_response, formatted_json=None):
        for k, v in req_response.__dict__.items():
            self.__dict__[k] = v
        self._formatted = formatted_json

    @property
    def formatted(self):
        return self._formatted

    @formatted.setter
    def formatted(self, value):
        self._formatted = value


if __name__ == '__main__':
    from bitex import Kraken

    k = Kraken()
    resp = k.ticker('XXBTZEUR')
    print(resp.formatted)
    print(resp.json())