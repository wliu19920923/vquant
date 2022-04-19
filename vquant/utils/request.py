import requests


class Request:
    GET, POST, PUT, DELETE = 'GET', 'POST', 'PUT', 'DELETE'

    @staticmethod
    def http_requests(method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        try:
            result = response.json()
        except Exception as exp:
            raise TypeError(response.text, exp)
        else:
            return result
