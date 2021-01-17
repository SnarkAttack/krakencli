import pytest
from krakencli.kraken_session import (
    KrakenSession,
    KrakenRequestManager,
    DEFAULT_KRAKEN_API_DOMAIN,
    DEFAULT_KRAKEN_API_VERSION
)
from krakencli.exceptions import (
    InvalidPublicEndpointException,
    InvalidPrivateEndpointException,
)


def test_init_default():
    req_man = KrakenRequestManager()
    assert req_man._api_domain == DEFAULT_KRAKEN_API_DOMAIN
    assert req_man._api_version == DEFAULT_KRAKEN_API_VERSION


def test_get_nonces():
    req_man = KrakenRequestManager()
    nonce1 = req_man.get_next_nonce()
    nonce2 = req_man.get_next_nonce()
    assert nonce1 > 0
    assert nonce2 > 0
    assert nonce1 < nonce2


def test_public_request_bad_endpoint():
    req_man = KrakenRequestManager()
    with pytest.raises(InvalidPublicEndpointException):
        req_man.make_public_request("bad_request", {})


def test_private_request_bad_endpoint():
    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')
    req_man = sess._request_manager
    with pytest.raises(InvalidPrivateEndpointException):
        req_man.make_private_request("bad_priv_request", {})
