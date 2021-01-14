from .kraken_api_values import KRAKEN_VALID_PUBLIC_ENDPOINTS


class InvalidKeyFileException(Exception):

    def __init__(self, file_path):
        self.file_path = file_path
        super().__init__(f"Key file {self.file_path} is "
                         f"not formatted properly")


class InvalidPublicEndpointException(Exception):

    def __init__(self, bad_endpoint):
        self.bad_endpoint = bad_endpoint
        super().__init__(f"'{self.bad_endpoint}' is not a valid endpoint. "
                         f"Please use one of the following endpoints: "
                         f"{KRAKEN_VALID_PUBLIC_ENDPOINTS}")


class MissingRequiredParameterException(Exception):

    def __init__(self, param_name, request_type=None):
        self.param_name = param_name
        self.request_type = request_type
        super().__init__(f"'{self.param_name}' is a required parameter for "
                         f"a(n) '{self.request_type}' request.")


class InvalidRequestParameterException(Exception):

    def __init__(self,
                 param_name,
                 param_value,
                 valid_values,
                 request_type=None):
        self.param_name = param_name
        self.param_value = param_value
        self.valid_values = valid_values
        self.request_type = request_type
        super().__init__((f"'{self.param_value}' is an invalid option for the "
                          f"'{self.param_name}' parameter in a(n) "
                          f"'{self.request_type}' request. Please use one of "
                          f"the following values: {self.valid_values}"))
