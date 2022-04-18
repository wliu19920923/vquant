import requests


class Request:
    GET, POST, PUT, DELETE = 'GET', 'POST', 'PUT', 'DELETE'

    @staticmethod
    def http_requests(method, url, **kwargs):
        params = kwargs.get('params') or dict()
        headers = kwargs.get('headers')
        response = requests.request(method, url, params=params, headers=headers)
        try:
            result = response.json()
        except Exception as exp:
            raise TypeError(response.text, exp)
        else:
            return result
