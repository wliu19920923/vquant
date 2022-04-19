def exception_catcher(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as exp:
            self.logger.error(str(exp))

    return wrapper
