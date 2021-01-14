import requests
from datetime import datetime
from .exceptions import (
    InvalidPublicEndpointException,
    InvalidKeyFileException,
    MissingRequiredParameterException,
    InvalidRequestParameterException,
    InvalidTimestampException
)
from .kraken_api_values import (
    KRAKEN_VALID_PUBLIC_ENDPOINTS,
    KRAKEN_ASSET_PAIRS
)

DEFAULT_KRAKEN_API_DOMAIN = "https://api.kraken.com"
DEFAULT_KRAKEN_API_VERSION = 0
DEFAULT_KRAKEN_API_PUBLIC_ADDRESS = "public"
DEFAULT_KRAKEN_API_PRIVATE_ADDRESS = "private"


class KrakenRequestManager(object):

    def __init__(self,
                 api_domain=DEFAULT_KRAKEN_API_DOMAIN,
                 api_version=DEFAULT_KRAKEN_API_VERSION):
        self._api_domain = api_domain
        self._api_version = api_version
        self._prev_nonce = 0

    def generate_nonce(self):
        return int(datetime.utcnow().timestamp()*100)

    def get_next_nonce(self):
        nonce = self.generate_nonce()
        while nonce <= self._prev_nonce:
            nonce = self.generate_nonce()
        print(nonce)
        self._prev_nonce = nonce
        return nonce

    def build_url(self, pub_priv, endpoint):
        return f"{self._api_domain}/{self._api_version}/{pub_priv}/{endpoint}"

    def build_public_url(self, endpoint):
        return self.build_url(DEFAULT_KRAKEN_API_PUBLIC_ADDRESS, endpoint)

    def build_private_address(self, endpoint):
        return self.build_url(DEFAULT_KRAKEN_API_PRIVATE_ADDRESS, endpoint)

    def make_public_request(self, endpoint, request_data={}):
        if endpoint not in KRAKEN_VALID_PUBLIC_ENDPOINTS:
            raise InvalidPublicEndpointException(endpoint)

        url = self.build_public_url(endpoint)

        response = requests.get(url, params=request_data)
        return response.json()['result']


class KrakenSession(object):

    def __init__(self,
                 api_domain=DEFAULT_KRAKEN_API_DOMAIN,
                 api_version=DEFAULT_KRAKEN_API_VERSION,
                 api_key=None,
                 private_key=None):
        self._request_manager = KrakenRequestManager(api_domain, api_version)
        self._api_key = api_key
        self._private_key = private_key

    def set_api_key(self, api_key):
        self._api_key = api_key

    def set_private_key(self, private_key):
        self._private_key = private_key

    def load_keys_from_file(self, file_path):
        with open(file_path, "r") as f:
            try:
                [self._api_key, self._private_key] = (
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

    def _validate_user_parameter_value(self,
                                       name,
                                       value,
                                       valid_options,
                                       required):
        base_validation = self._validate_user_parameter_base(name, value, required)
        if base_validation == value:
            if value is not None and value not in valid_options:
                raise InvalidRequestParameterException(name, value, valid_options)
            else:
                return value
        else:
            return base_validation

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
        if base_validation == comma_delimited_value:
            if comma_delimited_value is not None:
                value_list = comma_delimited_value.split(',')
                if all(value in valid_options for value in value_list):
                    return comma_delimited_value
                else:
                    raise InvalidRequestParameterException(
                        name,
                        comma_delimited_value,
                        valid_options
                    )
            else:
                return base_validation

    def _validate_user_parameter_timestamp(self, name, value, required):
        base_validation = self._validate_user_parameter_base(name, value, required)
        if base_validation == value:
            if value is not None:
                now_timestamp = datetime.utcnow().timestamp()
                if value-now_timestamp > 0:
                    raise InvalidTimestampException(name, value)
                else:
                    return value
            else:
                return None
        else:
            return base_validation

    def get_server_time(self):
        return self._request_manager.make_public_request("Time")

    def get_system_status(self):
        return self._request_manager.make_public_request("SystemStatus")

    def get_asset_info(self, info=None, aclass=None):

        valid_info_options = ['info']
        valid_aclass_options = ['currency']

        data = {}

        try:
            data['info'] = self._validate_user_parameter_value('info',
                                                               info,
                                                               valid_info_options,
                                                               False)
            data['aclass'] = self._validate_user_parameter_value('aclass',
                                                                 aclass,
                                                                 valid_aclass_options,
                                                                 False)
        except InvalidRequestParameterException as e:
            raise InvalidRequestParameterException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetAssetInfo')

        return self._request_manager.make_public_request('Assets', data)

    def get_tradable_asset_pairs(self, info=None, pair=None):

        valid_info_options = ['info', 'leverage', 'fees', 'margin']
        valid_asset_pairs = KRAKEN_ASSET_PAIRS

        data = {}

        try:
            data['info'] = self._validate_user_parameter_value('info',
                                                               info,
                                                               valid_info_options,
                                                               False)
            data['pair'] = self._validate_user_parameter_comma_delimited(
                                                                    'pair',
                                                                    pair,
                                                                    valid_asset_pairs,
                                                                    False)
        except InvalidRequestParameterException as e:
            raise InvalidRequestParameterException(e.param_name,
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
        except InvalidRequestParameterException as e:
            raise InvalidRequestParameterException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetTickerInformation')

        return self._request_manager.make_public_request('Ticker', data)

    def get_ohlc_data(self, pair, interval=None, since=None):

        valid_asset_pairs = KRAKEN_ASSET_PAIRS
        valid_time_interval = [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]

        data = {}

        try:
            data['pair'] = self._validate_user_parameter_value(
                'pair',
                pair,
                valid_asset_pairs,
                True
            )
            data['interval'] = self._validate_user_parameter_value(
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
        except InvalidRequestParameterException as e:
            raise InvalidRequestParameterException(e.param_name,
                                                   e.param_value,
                                                   e.valid_values,
                                                   'GetOHLCData')
        except InvalidTimestampException as e:
            raise InvalidTimestampException(e.param_name,
                                            e.param_value,
                                            'GetOHLCData')

        return self._request_manager.make_public_request("OHLC", data)
