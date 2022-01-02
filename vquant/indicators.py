import talib
from vquant.datafeed import DataFeed


class CCI(DataFeed):
    def __init__(self, data, period):
        data = talib.CCI(data.high.values, data.low.values, data.close.values, timeperiod=period)
        super(CCI, self).__init__(data)


class KDJ(object):
    def __init__(self, data):
        self.__data = talib.STOCH(data.high.values, data.low.values, data.close.values, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        self.k = DataFeed(self.__data[0])
        self.d = DataFeed(self.__data[1])
        self.j = DataFeed(3 * talib.STOCH(self.__data[0] - 2 * self.__data[1]))


class MA(DataFeed):
    def __init__(self, data, period):
        data = talib.MA(data.close.values, timeperiod=period)
        super(MA, self).__init__(data)


class EMA(DataFeed):
    def __init__(self, data, period):
        data = talib.EMA(data.close.values, timeperiod=period)
        super(EMA, self).__init__(data)


class SMA(DataFeed):
    def __init__(self, data, period):
        data = talib.SMA(data.close.values, timeperiod=period)
        super(SMA, self).__init__(data)
