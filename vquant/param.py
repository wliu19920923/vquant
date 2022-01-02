class Param(object):
    def __init__(self, params: tuple):
        for key, value in params:
            setattr(self, key, value)
