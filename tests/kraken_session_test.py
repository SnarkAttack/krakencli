import pytest
from krakencli.kraken_session import KrakenSession, DEFAULT_KRAKEN_API_DOMAIN, DEFAULT_KRAKEN_API_VERSION
from krakencli.exceptions import *

def test_kraken_session_init_default():
    sess = KrakenSession()
    assert sess._api_domain == DEFAULT_KRAKEN_API_DOMAIN
    assert sess._api_version == DEFAULT_KRAKEN_API_VERSION

def test_kraken_session_load_keys_from_file():
    sess = KrakenSession()
    sess.load_keys_from_file('tests/test_kraken.key')
    assert sess._api_key == "testapikey"
    assert sess._private_key == "testprivatekey"

def test_kraken_session_load_keys_from_file_bad():
    sess = KrakenSession()
    with pytest.raises(InvalidKeyFile):
        sess.load_keys_from_file('tests/bad_test_kraken.key')
