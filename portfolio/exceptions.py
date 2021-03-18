from rest_framework.exceptions import APIException


class AssetTickerNonExist(APIException):
    status_code = 404
    default_detail = 'Ticker non-exist'
    default_code = 'ticker_nonexist'
