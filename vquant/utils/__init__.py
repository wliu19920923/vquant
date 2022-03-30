class Params(object):
    def __init__(self, params: tuple):
        for key, value in params:
            setattr(self, key, value)


class RequestMethod(object):
    GET, POST, PUT, DELETE = 'GET', 'POST', 'PUT', 'DELETE'


def exception_catcher(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as exp:
            self.logger.error(str(exp))

    return wrapper
