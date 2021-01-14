import pytest
from krakencli.kraken_session import (
    KrakenSession,
    KrakenRequestManager,
    DEFAULT_KRAKEN_API_DOMAIN,
    DEFAULT_KRAKEN_API_VERSION
)
from krakencli.exceptions import (
    InvalidKeyFileException,
    InvalidPublicEndpointException,
    InvalidRequestParameterException,
    MissingRequiredParameterException
)
from tests.test_utilities import lists_match, list_in_list


def test_kraken_request_manager_init_default():
    req_man = KrakenRequestManager()
    assert req_man._api_domain == DEFAULT_KRAKEN_API_DOMAIN
    assert req_man._api_version == DEFAULT_KRAKEN_API_VERSION


def test_kraken_request_manager_get_nonces():
    req_man = KrakenRequestManager()
    nonce1 = req_man.get_next_nonce()
    nonce2 = req_man.get_next_nonce()
    assert nonce1 > 0
    assert nonce2 > 0
    assert nonce1 < nonce2


def test_kraken_request_manager_public_request_bad_endpoint():
    req_man = KrakenRequestManager()
    with pytest.raises(InvalidPublicEndpointException):
        req_man.make_public_request("bad_request", {})


def test_kraken_session_set_api_key():
    sess = KrakenSession()
    sess.set_api_key("tempapikey")
    assert sess._api_key == "tempapikey"


def test_kraken_session_set_private_key():
    sess = KrakenSession()
    sess.set_private_key("tempprivatekey")
    assert sess._private_key == "tempprivatekey"


def test_kraken_session_load_keys_from_file():
    sess = KrakenSession()
    sess.load_keys_from_file('tests/test_kraken.key')
    assert sess._api_key == "testapikey"
    assert sess._private_key == "testprivatekey"


def test_kraken_session_load_keys_from_file_bad():
    sess = KrakenSession()
    with pytest.raises(InvalidKeyFileException):
        sess.load_keys_from_file('tests/bad_test_kraken.key')


def test_kraken_session_get_server_time():
    sess = KrakenSession()
    server_time = sess.get_server_time()
    assert sorted(server_time.keys()) == sorted(['unixtime', 'rfc1123'])


def test_kraken_session_get_system_status():
    sess = KrakenSession()
    system_status = sess.get_system_status()
    assert sorted(system_status.keys()) == sorted(['status', 'timestamp'])


def test_kraken_session_get_asset_info():

    expected_keys = ['altname', 'aclass', 'decimals', 'display_decimals']

    sess = KrakenSession()
    asset_info = sess.get_asset_info()
    for asset in asset_info.values():
        assert lists_match(asset.keys(), expected_keys)
    asset_info_info_param = sess.get_asset_info(info='info')
    for asset in asset_info_info_param.values():
        assert lists_match(asset.keys(), expected_keys)
    with pytest.raises(InvalidRequestParameterException):
        sess.get_asset_info(info='unknown')
    asset_info_aclass_param = sess.get_asset_info(aclass='currency')
    for asset in asset_info_aclass_param.values():
        assert lists_match(asset.keys(), expected_keys)
    with pytest.raises(InvalidRequestParameterException):
        sess.get_asset_info(aclass='unknown')


def test_kraken_session_tradable_asset_pairs():

    all_possible_keys = [
        'aclass_base',
        'aclass_quote',
        'altname',
        'base',
        'fee_volume_currency',
        'fees',
        'fees_maker',
        'leverage_buy',
        'leverage_sell',
        'lot',
        'lot_decimals',
        'lot_multiplier',
        'margin_call',
        'margin_stop',
        'ordermin',
        'pair_decimals',
        'quote',
        'wsname',
    ]

    sess = KrakenSession()
    asset_pairs = sess.get_tradable_asset_pairs()
    for asset in asset_pairs.values():
        assert list_in_list(asset.keys(), all_possible_keys)

    # Test all variations for info parameter
    asset_pairs_info = sess.get_tradable_asset_pairs(info='info')
    for asset in asset_pairs_info.values():
        assert list_in_list(asset.keys(), all_possible_keys)
    asset_pairs_leverage = sess.get_tradable_asset_pairs(info='leverage')
    for asset in asset_pairs_leverage.values():
        assert list_in_list(asset.keys(), all_possible_keys)
    asset_pairs_fees = sess.get_tradable_asset_pairs(info='fees')
    for asset in asset_pairs_fees.values():
        assert list_in_list(asset.keys(), all_possible_keys)
    asset_pairs_margin = sess.get_tradable_asset_pairs(info='margin')
    for asset in asset_pairs_margin.values():
        assert list_in_list(asset.keys(), all_possible_keys)
    with pytest.raises(InvalidRequestParameterException):
        sess.get_tradable_asset_pairs(info='bad')

    # Test use of comma delimited lists of a few lengths

    single_list = ['XXDGXXBT']
    single_list_as_string = ','.join(single_list)
    asset_pairs_single = sess.get_tradable_asset_pairs(pair=single_list_as_string)
    assert lists_match(asset_pairs_single.keys(), single_list)

    multi_list = ['XETHZUSD', 'USDTEUR', 'KAVAEUR']
    multi_list_as_string = ','.join(multi_list)
    asset_pairs_multi = sess.get_tradable_asset_pairs(pair=multi_list_as_string)
    assert lists_match(asset_pairs_multi.keys(), multi_list)

    bad_list = ['PAXGXBT', 'XLTCZEUR', 'GNOXBT', 'BADPAIR']
    with pytest.raises(InvalidRequestParameterException):
        bad_list_as_string = ','.join(bad_list)
        sess.get_tradable_asset_pairs(pair=bad_list_as_string)


def test_kraken_session_get_ticker_information():

    sess = KrakenSession()

    with pytest.raises(MissingRequiredParameterException):
        sess.get_ticker_information(None)

    single_list = ['XXDGXXBT']
    single_list_as_string = ','.join(single_list)
    asset_pairs_single = sess.get_ticker_information(pair=single_list_as_string)
    assert lists_match(asset_pairs_single.keys(), single_list)

    multi_list = ['XETHZUSD', 'USDTEUR', 'KAVAEUR']
    multi_list_as_string = ','.join(multi_list)
    asset_pairs_multi = sess.get_ticker_information(pair=multi_list_as_string)
    assert lists_match(asset_pairs_multi.keys(), multi_list)

    bad_list = ['PAXGXBT', 'XLTCZEUR', 'GNOXBT', 'BADPAIR']
    with pytest.raises(InvalidRequestParameterException):
        bad_list_as_string = ','.join(bad_list)
        sess.get_ticker_information(pair=bad_list_as_string)
