class DataFeed(object):
    def __init__(self, data):
        self.__data = data

    def __getitem__(self, item: int):
        return self.__data[item - 1]


class KLineData(object):
    def __init__(self, data):
        self.timestamp = DataFeed(data.open.values)
        self.open = DataFeed(data.open.values)
        self.high = DataFeed(data.high.values)
        self.low = DataFeed(data.low.values)
        self.close = DataFeed(data.close.values)
        self.volume = DataFeed(data.volume.values)
