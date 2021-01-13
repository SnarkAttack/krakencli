from .exceptions import *

DEFAULT_KRAKEN_API_DOMAIN = "https://api.kraken.com"
DEFAULT_KRAKEN_API_VERSION = 0
DEFAULT_KRAKEN_API_PUBLIC_ADDRESS = "public"
DEFAULT_KRAKEN_API_PRIVATE_ADDRESS = "private"

class KrakenSession(object):

    def __init__(self,
                 api_domain=DEFAULT_KRAKEN_API_DOMAIN,
                 api_version=DEFAULT_KRAKEN_API_VERSION,
                 api_key=None,
                 private_key=None
                ):
        self._api_domain = api_domain
        self._api_version = api_version
        self._api_key = api_key
        self._private_key = private_key

    def set_api_key(self, api_key):
        self._api_key = api_key

    def set_private_key(self, private_key):
        self._private_key = private_key

    def load_keys_from_file(self, file_path):
        with open(file_path, "r") as f:
            try:
                [self._api_key, self._private_key] = [next(f).strip() for x in range(2)]
            except StopIteration as s:
                raise InvalidKeyFile(file_path)

if __name__ == "__main__":
    sess = KrakenSession()
    sess.load_keys_from_file('tests/bad_test_kraken.key')
