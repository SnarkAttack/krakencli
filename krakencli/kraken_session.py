import requests
import hmac
import base64
import urllib.parse
from hashlib import sha256, sha512
import time
from .exceptions import (
    InvalidPublicEndpointException,
    InvalidPrivateEndpointException,
    InvalidKeyFileException,
    MissingRequiredParameterException,
    InvalidRequestParameterException,
    InvalidRequestParameterOptionsException,
    InvalidTimestampException,
    NoApiKeysException,
)
from .kraken_api_values import (
    KRAKEN_VALID_PUBLIC_ENDPOINTS,
    KRAKEN_VALID_PRIVATE_ENDPOINTS,
    KRAKEN_ASSETS,
    KRAKEN_ASSET_PAIRS
)

DEFAULT_KRAKEN_API_DOMAIN = "https://api.kraken.com"
DEFAULT_KRAKEN_API_VERSION = 0
DEFAULT_KRAKEN_API_PUBLIC_ADDRESS = "public"
DEFAULT_KRAKEN_API_PRIVATE_ADDRESS = "private"


class KrakenRequestManager(object):

    def __init__(self,
                 api_domain=DEFAULT_KRAKEN_API_DOMAIN,
                 api_version=DEFAULT_KRAKEN_API_VERSION,
                 api_key=None,
                 private_key=None):
        self._api_domain = api_domain
        self._api_version = api_version
        self._prev_nonce = 0
        self._api_key = api_key
        self._private_key = private_key

    def generate_nonce(self):
        return int(time.time() * 1000)

    def get_next_nonce(self):
        nonce = self.generate_nonce()
        while nonce <= self._prev_nonce:
            nonce = self.generate_nonce()
        self._prev_nonce = nonce
        return nonce

    def build_url(self, pub_priv, endpoint):
        return f"{self._api_domain}/{self._api_version}/{pub_priv}/{endpoint}"

    def build_public_url(self, endpoint):
        return self.build_url(DEFAULT_KRAKEN_API_PUBLIC_ADDRESS, endpoint)

    def build_private_url(self, endpoint):
        return self.build_url(DEFAULT_KRAKEN_API_PRIVATE_ADDRESS, endpoint)

    def _make_private_request_headers(self, url, post_data):

        headers = {}
        headers['API-Key'] = self._api_key

        url_encoded_post_data = urllib.parse.urlencode(post_data)
        nonce = post_data['nonce']
        internal_data = (str(nonce)+url_encoded_post_data).encode()

        private_key_b64_dec = base64.b64decode(self._private_key)
        uri = '/'+url.lstrip(self._api_domain)
        enc_url = uri.encode()
        internal_sha256 = sha256(internal_data).digest()
        msg = enc_url+internal_sha256

        h = hmac.new(private_key_b64_dec, msg, sha512)
        h = base64.b64encode(h.digest())
        h = h.decode()
        headers['API-Sign'] = h

        return headers

    def make_public_request(self, endpoint, request_data={}):
        if endpoint not in KRAKEN_VALID_PUBLIC_ENDPOINTS:
            raise InvalidPublicEndpointException(endpoint)

        url = self.build_public_url(endpoint)

        response = requests.get(url, params=request_data)
        return response.json()['result']

    def make_private_request(self, endpoint, request_data={}):
        if self._api_key is None or self._private_key is None:
            raise NoApiKeysException()
        if endpoint not in KRAKEN_VALID_PRIVATE_ENDPOINTS:
            raise InvalidPrivateEndpointException(endpoint)
        url = self.build_private_url(endpoint)

        nonce = self.get_next_nonce()

        post_data = {}
        post_data['nonce'] = nonce

        headers = self._make_private_request_headers(url, post_data)

        response = requests.post(url, headers=headers, data=post_data)

        # TODO: REthink how results are returned, there are some cases where a valid
        # API call exists and returns a 200 status code without a result field
        # (Example is calling balance on account with no balance)
        return response.json()['result']


class KrakenSession(object):

    def __init__(self,
                 api_domain=DEFAULT_KRAKEN_API_DOMAIN,
                 api_version=DEFAULT_KRAKEN_API_VERSION,
                 api_key=None,
                 private_key=None):
        self._request_manager = KrakenRequestManager(
            api_domain,
            api_version,
            api_key,
            private_key
        )

    def set_api_key(self, api_key):
        self._request_manager._api_key = api_key

    def set_private_key(self, private_key):
        self._request_manager._private_key = private_key

    def load_keys_from_file(self, file_path):
        with open(file_path, "r") as f:
            try:
                [self._request_manager._api_key, self._request_manager._private_key] = (
                    [next(f).strip() for x in range(2)]
                )
            except StopIteration:
                raise InvalidKeyFileException(file_path)

    def _validate_user_parameter_base(self, name, value, required):
        if value is None:
            if required:
                raise MissingRequiredParameterException(name)
            else:
                return None
        else:
            return value

    def _validate_user_parameter_options(self,
                                         name,
                                         value,
                                         valid_options,
                                         required):
        base_validation = self._validate_user_parameter_base(name, value, required)
        if base_validation is None:
            return None
        else:
            if base_validation == value:
                if value in valid_options:
                    return value
            raise InvalidRequestParameterOptionsException(
                name,
                value,
                valid_options
            )

    def _validate_user_parameter_comma_delimited(self,
                                                 name,
                                                 comma_delimited_value,
                                                 valid_options,
                                                 required):
        base_validation = self._validate_user_parameter_base(
            name,
            comma_delimited_value,
            required
        )
        if base_validation is None:
            return None
        else:
            if base_validation == comma_delimited_value:
                value_list = comma_delimited_value.split(',')
                if all(value in valid_options for value in value_list):
                    return comma_delimited_value
            raise InvalidRequestParameterOptionsException(
                name,
                comma_delimited_value,
                valid_options
            )

    def _validate_user_parameter_timestamp(self, name, value, required):
        base_validation = self._validate_user_parameter_base(name, value, required)
        if base_validation is None:
            return None
        else:
            if base_validation == value:
                if isinstance(value, float) or isinstance(value, int):
                    return value
            raise InvalidTimestampException(name, value)

    def _validate_user_parameter_integer(self, name, value, required):
        base_validation = self._validate_user_parameter_base(name, value, required)
        if base_validation is None:
            return None
        if base_validation == value:
            if isinstance(value, int):
                return value
            raise InvalidRequestParameterException(name, value)

    def get_server_time(self):
        return self._request_manager.make_public_request("Time")

    def get_system_status(self):
        return self._request_manager.make_public_request("SystemStatus")

    def get_asset_info(self, info=None, aclass=None):

        valid_info_options = ['info']
        valid_aclass_options = ['currency']

        data = {}

        try:
            data['info'] = self._validate_user_parameter_options(
                'info',
                info,
                valid_info_options,
                False
            )
            data['aclass'] = self._validate_user_parameter_options(
                'aclass',
                aclass,
                valid_aclass_options,
                False
            )
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetAssetInfo')

        return self._request_manager.make_public_request('Assets', data)

    def get_tradable_asset_pairs(self, info=None, pair=None):

        valid_info_options = ['info', 'leverage', 'fees', 'margin']
        valid_asset_pairs = KRAKEN_ASSET_PAIRS

        data = {}

        try:
            data['info'] = self._validate_user_parameter_options(
                'info',
                info,
                valid_info_options,
                False
            )
            data['pair'] = self._validate_user_parameter_comma_delimited(
                'pair',
                pair,
                valid_asset_pairs,
                False
            )
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetTradableAssetPairs')

        return self._request_manager.make_public_request('AssetPairs', data)

    def get_ticker_information(self, pair):

        valid_asset_pairs = KRAKEN_ASSET_PAIRS

        data = {}

        try:
            data['pair'] = self._validate_user_parameter_comma_delimited(
                'pair',
                pair,
                valid_asset_pairs,
                True)
        except MissingRequiredParameterException as e:
            raise MissingRequiredParameterException(e.param_name,
                                                    'GetTickerInformation')
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetTickerInformation')

        return self._request_manager.make_public_request('Ticker', data)

    def get_ohlc_data(self, pair, interval=None, since=None):

        valid_asset_pairs = KRAKEN_ASSET_PAIRS
        valid_time_interval = [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]

        data = {}

        try:
            data['pair'] = self._validate_user_parameter_options(
                'pair',
                pair,
                valid_asset_pairs,
                True
            )
            data['interval'] = self._validate_user_parameter_options(
                'interval',
                interval,
                valid_time_interval,
                False
            )
            data['since'] = self._validate_user_parameter_timestamp(
                'since',
                since,
                False
            )
        except MissingRequiredParameterException as e:
            raise MissingRequiredParameterException(e.param_name,
                                                    'GetOHLCData')
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetOHLCData')
        except InvalidTimestampException as e:
            raise InvalidTimestampException(e.param_name,
                                            e.param_value,
                                            'GetOHLCData')

        return self._request_manager.make_public_request("OHLC", data)

    def get_order_book(self, pair, count=None):

        valid_asset_pairs = KRAKEN_ASSET_PAIRS

        data = {}

        try:
            data['pair'] = self._validate_user_parameter_options(
                'pair',
                pair,
                valid_asset_pairs,
                True
            )
            data['count'] = self._validate_user_parameter_integer(
                'count',
                count,
                False
            )
        except MissingRequiredParameterException as e:
            raise MissingRequiredParameterException(
                e.param_name,
                'GetOrderBook'
            )
        except InvalidRequestParameterException as e:
            raise InvalidRequestParameterException(
                e.param_name,
                e.param_value,
                'GetOrderBook'
            )
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(
                e.param_name,
                e.param_value,
                e.valid_values,
                'GetOrderBook'
            )

        return self._request_manager.make_public_request('Depth', data)

    def get_recent_trades(self, pair, since=None):

        valid_asset_pairs = KRAKEN_ASSET_PAIRS

        data = {}

        try:
            data['pair'] = self._validate_user_parameter_options(
                'pair',
                pair,
                valid_asset_pairs,
                True
            )
            data['since'] = self._validate_user_parameter_timestamp(
                'since',
                since,
                False
            )
        except MissingRequiredParameterException as e:
            raise MissingRequiredParameterException(e.param_name,
                                                    'GetRecentTrades')
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                          e.param_value,
                                                          e.valid_values,
                                                          'GetRecentTrades')
        except InvalidTimestampException as e:
            raise InvalidTimestampException(e.param_name,
                                            e.param_value,
                                            'GetRecentTrades')

        return self._request_manager.make_public_request('Trades', data)

    def get_recent_spread_data(self, pair, since=None):

        valid_asset_pairs = KRAKEN_ASSET_PAIRS

        data = {}

        try:
            data['pair'] = self._validate_user_parameter_options(
                'pair',
                pair,
                valid_asset_pairs,
                True
            )
            data['since'] = self._validate_user_parameter_timestamp(
                'since',
                since,
                False
            )
        except MissingRequiredParameterException as e:
            raise MissingRequiredParameterException(e.param_name,
                                                    'GetRecentSpreadData')
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                          e.param_value,
                                                          e.valid_values,
                                                          'GetRecentSpreadData')
        except InvalidTimestampException as e:
            raise InvalidTimestampException(e.param_name,
                                            e.param_value,
                                            'GetRecentSpreadData')

        return self._request_manager.make_public_request('Spread', data)

    def get_account_balance(self):
        return self._request_manager.make_private_request('Balance')

    def get_trade_balance(self, aclass=None, asset=None):

        valid_aclass_options = ['currency']

        data = {}

        try:
            data['aclass'] = self._validate_user_parameter_options(
                'aclass',
                aclass,
                valid_aclass_options,
                False
            )
            data['asset'] = self._validate_user_parameter_options(
                'asset',
                asset,
                KRAKEN_ASSETS,
                False
            )
        except InvalidRequestParameterOptionsException as e:
            raise InvalidRequestParameterOptionsException(e.param_name,
                                                          e.param_value,
                                                          KRAKEN_ASSETS,
                                                          'GetTradeBalance')

        return self._request_manager.make_private_request('TradeBalance', data)
