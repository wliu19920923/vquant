import pandas
from vquant.analyzers import Analyzer


class Cerebro(object):
    def __init__(self, broker):
        self.datas = list()
        self.strategies = list()
        self.broker = broker(self)
        self.index = None

    def add_data(self, data):
        data['index'] = pandas.to_datetime(data['datetime'])
        data.set_index('index', inplace=True)
        self.datas.append(data)

    def add_strategy(self, strategy):
        self.strategies.append(strategy(self))

    def notify_order(self, order):
        for strategy in self.strategies:
            strategy.notify_order(order)

    def notify_trade(self, trade):
        for strategy in self.strategies:
            strategy.notify_trade(trade)

    def notify_position(self, position):
        for strategy in self.strategies:
            strategy.notify_position(position)

    def notify_profit(self, profit):
        for strategy in self.strategies:
            strategy.notify_profit(profit)

    def run(self):
        self.index = self.datas[0].iloc[0].datetime
        for row in self.datas[0].itertuples():
            self.index = row.datetime
            for strategy in self.strategies:
                strategy.next()
            self.broker.settlement()
        return Analyzer(self.broker)
