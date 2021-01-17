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
    InvalidPrivateEndpointException,
    InvalidRequestParameterException,
    InvalidRequestParameterOptionsException,
    MissingRequiredParameterException,
    InvalidTimestampException,
    NoApiKeysException
)
from tests.test_utilities import (
    lists_match,
    list_in_list,
    dict_value_length_check
)
from tests.test_defs import (
    ALL_POSSIBLE_ASSET_PAIR_KEYS,
    EXPECTED_ASSET_INFO_KEYS,
    TICKER_RESULTS_EXPECTED_LENGTH,
    OHLC_DATA_LENGTH,
    ORDER_BOOK_ASKS_LENGTH,
    ORDER_BOOKS_BIDS_LENGTH,
    RECENT_TRADES_LENGTH,
    RECENT_SPREAD_DATA_LENGTH,
    TRADE_BALANCE_RESULT_KEYS,
)

def test_set_api_key():
    sess = KrakenSession()
    sess.set_api_key("tempapikey")
    assert sess._request_manager._api_key == "tempapikey"


def test_set_private_key():
    sess = KrakenSession()
    sess.set_private_key("tempprivatekey")
    assert sess._request_manager._private_key == "tempprivatekey"


def test_load_keys_from_file():
    sess = KrakenSession()
    sess.load_keys_from_file('tests/test_kraken.key')
    assert sess._request_manager._api_key == "testapikey"
    assert sess._request_manager._private_key == "testprivatekey"


def test_load_keys_from_file_bad():
    sess = KrakenSession()
    with pytest.raises(InvalidKeyFileException):
        sess.load_keys_from_file('tests/bad_test_kraken.key')


def test_get_server_time():
    sess = KrakenSession()
    server_time = sess.get_server_time()
    assert sorted(server_time.keys()) == sorted(['unixtime', 'rfc1123'])


def test_get_system_status():
    sess = KrakenSession()
    system_status = sess.get_system_status()
    assert sorted(system_status.keys()) == sorted(['status', 'timestamp'])


def test_get_asset_info_base():

    sess = KrakenSession()
    asset_info = sess.get_asset_info()
    for asset in asset_info.values():
        assert lists_match(asset.keys(), EXPECTED_ASSET_INFO_KEYS)


def test_get_asset_info_info():

    sess = KrakenSession()
    asset_info_info_param = sess.get_asset_info(info='info')
    for asset in asset_info_info_param.values():
        assert lists_match(asset.keys(), EXPECTED_ASSET_INFO_KEYS)
    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_asset_info(info='unknown')


def test_get_asset_info_aclass():

    sess = KrakenSession()
    asset_info_aclass_param = sess.get_asset_info(aclass='currency')
    for asset in asset_info_aclass_param.values():
        assert lists_match(asset.keys(), EXPECTED_ASSET_INFO_KEYS)
    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_asset_info(aclass='unknown')


def test_get_tradable_asset_pairs_base():

    sess = KrakenSession()
    asset_pairs = sess.get_tradable_asset_pairs()
    for asset in asset_pairs.values():
        assert list_in_list(asset.keys(), ALL_POSSIBLE_ASSET_PAIR_KEYS)


def test_get_tradable_asset_pairs_info():

    sess = KrakenSession()
    asset_pairs_info = sess.get_tradable_asset_pairs(info='info')
    for asset in asset_pairs_info.values():
        assert list_in_list(asset.keys(), ALL_POSSIBLE_ASSET_PAIR_KEYS)
    asset_pairs_leverage = sess.get_tradable_asset_pairs(info='leverage')
    for asset in asset_pairs_leverage.values():
        assert list_in_list(asset.keys(), ALL_POSSIBLE_ASSET_PAIR_KEYS)
    asset_pairs_fees = sess.get_tradable_asset_pairs(info='fees')
    for asset in asset_pairs_fees.values():
        assert list_in_list(asset.keys(), ALL_POSSIBLE_ASSET_PAIR_KEYS)
    asset_pairs_margin = sess.get_tradable_asset_pairs(info='margin')
    for asset in asset_pairs_margin.values():
        assert list_in_list(asset.keys(), ALL_POSSIBLE_ASSET_PAIR_KEYS)
    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_tradable_asset_pairs(info='bad')


def test_get_tradable_asset_pairs_pair():

    sess = KrakenSession()
    single_list = ['XXDGXXBT']
    single_list_as_string = ','.join(single_list)
    asset_pairs_single = sess.get_tradable_asset_pairs(pair=single_list_as_string)
    assert lists_match(asset_pairs_single.keys(), single_list)

    multi_list = ['XETHZUSD', 'USDTEUR', 'KAVAEUR']
    multi_list_as_string = ','.join(multi_list)
    asset_pairs_multi = sess.get_tradable_asset_pairs(pair=multi_list_as_string)
    assert lists_match(asset_pairs_multi.keys(), multi_list)

    bad_list = ['PAXGXBT', 'XLTCZEUR', 'GNOXBT', 'BADPAIR']
    with pytest.raises(InvalidRequestParameterOptionsException):
        bad_list_as_string = ','.join(bad_list)
        sess.get_tradable_asset_pairs(pair=bad_list_as_string)


def test_get_ticker_information():

    sess = KrakenSession()

    with pytest.raises(MissingRequiredParameterException):
        sess.get_ticker_information(None)

    single_pair = 'XXDGXXBT'
    single_list = [single_pair]
    single_list_as_string = ','.join(single_list)
    asset_pairs_single = sess.get_ticker_information(pair=single_list_as_string)
    assert lists_match(asset_pairs_single.keys(), single_list)

    ticker_data_pair = asset_pairs_single[single_pair]
    assert lists_match(
        ticker_data_pair.keys(),
        ['a', 'b', 'c', 'v', 'p', 't', 'l', 'h', 'o']
    )

    for key in ticker_data_pair.keys():
        # 'o' represents opening value, which is not a list
        if key != 'o':
            assert dict_value_length_check(key,
                                        ticker_data_pair,
                                        TICKER_RESULTS_EXPECTED_LENGTH)

    multi_list = ['XETHZUSD', 'USDTEUR', 'KAVAEUR']
    multi_list_as_string = ','.join(multi_list)
    asset_pairs_multi = sess.get_ticker_information(pair=multi_list_as_string)
    assert lists_match(asset_pairs_multi.keys(), multi_list)

    bad_list = ['PAXGXBT', 'XLTCZEUR', 'GNOXBT', 'BADPAIR']
    with pytest.raises(InvalidRequestParameterOptionsException):
        bad_list_as_string = ','.join(bad_list)
        sess.get_ticker_information(pair=bad_list_as_string)


def test_get_ohlc_data_base():

    sess = KrakenSession()

    with pytest.raises(MissingRequiredParameterException):
        sess.get_ohlc_data(None)

    asset_pair = 'SCXBT'
    ohlc_data = sess.get_ohlc_data(asset_pair)
    assert lists_match(ohlc_data.keys(), [asset_pair, 'last'])

    ohlc_pair_data = ohlc_data[asset_pair]
    for time_data in ohlc_pair_data:
        assert len(time_data) == OHLC_DATA_LENGTH

    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_ohlc_data("BADPAIR")


def test_get_ohlc_data_interval():

    interval_mins = 60
    asset_pair = 'SCXBT'

    sess = KrakenSession()
    ohlc_data_interval = sess.get_ohlc_data(asset_pair, interval=interval_mins)
    ts_list = ohlc_data_interval[asset_pair]
    for i, timestamp_data in enumerate(ts_list):
        if i > 0:
            assert timestamp_data[0]-(interval_mins*60) == ts_list[i-1][0]
    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_ohlc_data(asset_pair, interval=49)


def test_get_ohlc_data_since():

    since_ts = 1610640300
    asset_pair = 'SCXBT'

    sess = KrakenSession()
    ohlc_data_since = sess.get_ohlc_data(asset_pair, since=since_ts)
    ts_list = ohlc_data_since[asset_pair]
    for timestamp_data in ts_list:
        assert timestamp_data[0] > since_ts
    with pytest.raises(InvalidTimestampException):
        sess.get_ohlc_data(asset_pair, since="badinput")


def test_get_order_book_base():

    asset_pair = "XXRPZCAD"

    sess = KrakenSession()
    order_book = sess.get_order_book(asset_pair)
    assert lists_match(order_book.keys(), [asset_pair])

    asset_pair_order_book = order_book[asset_pair]
    assert lists_match(asset_pair_order_book.keys(), ['asks', 'bids'])

    for ask in asset_pair_order_book['asks']:
        assert len(ask) == ORDER_BOOK_ASKS_LENGTH

    for bids in asset_pair_order_book['bids']:
        assert len(bids) == ORDER_BOOKS_BIDS_LENGTH

    with pytest.raises(MissingRequiredParameterException):
        sess.get_order_book(None)

    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_order_book("BadPAiR")


def test_get_order_book_count():

    asset_pair = "XXRPZCAD"
    count = 3

    sess = KrakenSession()
    order_book = sess.get_order_book(asset_pair, count=count)

    asset_pair_order_book = order_book[asset_pair]
    for order_lists in asset_pair_order_book.values():
        assert len(order_lists) <= count

    with pytest.raises(InvalidRequestParameterException):
        sess.get_order_book(asset_pair, "four")


def test_get_recent_trades_base():

    asset_pair = "OXTETH"

    sess = KrakenSession()
    recent_trades = sess.get_recent_trades(asset_pair)

    assert lists_match(recent_trades.keys(), [asset_pair, 'last'])

    recent_trades_pair = recent_trades[asset_pair]
    for trade in recent_trades_pair:
        assert len(trade) == RECENT_TRADES_LENGTH

    with pytest.raises(MissingRequiredParameterException):
        sess.get_recent_trades(None)

    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_recent_trades("UNKCURR")


def test_get_recent_trades_since():

    asset_pair = "OXTETH"
    since = 1610660648.5366

    sess = KrakenSession()
    recent_trades = sess.get_recent_trades(asset_pair, since=since)

    for trade in recent_trades[asset_pair]:
        assert trade[2] >= since

    with pytest.raises(InvalidTimestampException):
        sess.get_recent_trades(asset_pair, since="11-12-20")


def test_get_recent_spead_data_base():

    asset_pair = "ETH2.SETH"

    sess = KrakenSession()
    recent_spread_data = sess.get_recent_spread_data(asset_pair)

    assert lists_match(recent_spread_data.keys(), [asset_pair, 'last'])

    recent_pair_spread_data = recent_spread_data[asset_pair]

    for spread_data in recent_pair_spread_data:
        assert len(spread_data) == RECENT_SPREAD_DATA_LENGTH

    with pytest.raises(MissingRequiredParameterException):
        sess.get_recent_spread_data(None)

    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_recent_spread_data("EXXDEE")


def test_get_recent_spread_data_since():

    asset_pair = "ETH2.SETH"
    since = 1610650690.1234

    sess = KrakenSession()
    recent_spread_data = sess.get_recent_spread_data(asset_pair, since=since)

    for spread_data in recent_spread_data[asset_pair]:
        assert spread_data[0] >= since

    with pytest.raises(InvalidTimestampException):
        sess.get_recent_spread_data(asset_pair, since="bad")

def test_private_request_no_keys():
    sess = KrakenSession()

    with pytest.raises(NoApiKeysException):
        sess.get_account_balance()


def test_get_account_balance_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    account_balance = sess.get_account_balance()
    assert isinstance(account_balance, dict)


def test_get_trade_balance_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    trade_balance = sess.get_trade_balance()
    assert lists_match(trade_balance.keys(), TRADE_BALANCE_RESULT_KEYS)


def tes_kraken_session_get_trade_balance_aclass():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    trade_balance = sess.get_trade_balance(aclass='currency')
    assert lists_match(trade_balance.keys(), TRADE_BALANCE_RESULT_KEYS)

    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_trade_balance(aclass="otherstuff")


def test_get_trade_balance_asset():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    trade_balance = sess.get_trade_balance(asset='ZCAD')
    assert lists_match(trade_balance.keys(), TRADE_BALANCE_RESULT_KEYS)

    with pytest.raises(InvalidRequestParameterOptionsException):
        sess.get_trade_balance(asset='FNYMN')


def test_get_open_orders_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    open_orders = sess.get_open_orders()
    assert lists_match(open_orders.keys(), ['open'])


def test_get_closed_orders_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_closed_orders()


def test_query_orders_info_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.query_orders_info(1)


def test_get_trades_history_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_trades_history()


def test_query_trade_info_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.query_trade_info(1)


def test_get_open_positions_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_open_positions(1)


def test_get_ledgers_info_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_ledgers_info()


def test_query_ledgers_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.query_ledgers(1)


def test_get_trade_volume_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_trade_volume()


def test_request_export_report_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.request_export_report("a", 2)


def test_get_export_statuses_bases():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_export_statuses(1)


def test_get_export_report_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_export_report(1)


def test_remove_export_report_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.remove_export_report(1, 1)


def test_add_standard_order_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.add_standard_order(1, 1, 1, 1)


def test_cancel_open_order_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.cancel_open_order(1)


def test_cancel_all_open_orders_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.cancel_all_open_orders()


def test_cancel_all_orders_after_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.cancel_all_orders_after(1)


def test_get_deposit_method_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_deposit_method(1)


def test_get_deposit_addresses_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_deposit_addresses(1, 1)


def test_get_deposit_status_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_deposit_status(1, 1)


def test_get_withdrawal_information_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_withdrawal_information(1, 1, 1)


def test_withdraw_funds_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.withdraw_funds(1, 1, 1)


def test_get_status_of_recent_withdrawals():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_status_of_recent_withdrawals(1, 1)


def test_request_withdrawal_cancellation_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.request_withdrawal_cancellation(1, 1)


def test_wallet_transfer_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.wallet_transfer(1, 1, 1, 1)


def test_get_web_socket_token_base():

    sess = KrakenSession()
    sess.load_keys_from_file('kraken.key')

    with pytest.raises(NotImplementedError):
        sess.get_web_socket_token()
