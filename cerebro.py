from vquant.datafeed import KLineData


class Cerebro(object):
    def __init__(self, broker, strategy):
        self.index = 0
        self.datas = list()
        self.broker = broker
        self.strategy = strategy

    def add_data(self, data):
        self.datas.append(data)

    @property
    def price(self):
        return self.datas[0].iloc[self.index].close

    @property
    def timestamp(self):
        return self.datas[0].iloc[self.index].timestamp

    def run(self):
        for i in range(len(self.datas[0])):
            self.index = i
            timestamp = self.datas[0].iloc[self.index].timestamp
            datas = list()
            for data in self.datas:
                ret = data.loc[data['timestamp'] <= timestamp]
                ret = KLineData(ret)
                datas.append(ret)
            self.strategy(self.broker, datas).run()
