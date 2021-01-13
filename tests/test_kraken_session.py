import pytest
from krakencli.kraken_session import KrakenSession, KrakenRequestManager, DEFAULT_KRAKEN_API_DOMAIN, DEFAULT_KRAKEN_API_VERSION
from krakencli.exceptions import *

def test_kraken_request_manager_init_default():
    req_man = KrakenRequestManager()
    assert req_man._api_domain == DEFAULT_KRAKEN_API_DOMAIN
    assert req_man._api_version == DEFAULT_KRAKEN_API_VERSION

def test_kraken_session_set_api_key():
    req_man = KrakenSession()
    req_man.set_api_key("tempapikey")
    assert req_man._api_key == "tempapikey"

def test_kraken_session_load_keys_from_file():
    sess = KrakenSession()
    sess.load_keys_from_file('tests/test_kraken.key')
    assert sess._api_key == "testapikey"
    assert sess._private_key == "testprivatekey"

def test_kraken_session_load_keys_from_file_bad():
    sess = KrakenSession()
    with pytest.raises(InvalidKeyFile):
        sess.load_keys_from_file('tests/bad_test_kraken.key')
