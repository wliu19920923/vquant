class DataFeeds(object):
    def __init__(self, data):
        self.__data = data

    def __getitem__(self, item: int):
        return self.__data[item - 1]
