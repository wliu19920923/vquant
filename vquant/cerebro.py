import pandas
from vquant.analyzers import Analyzer
from vquant.broker import Order


class Cerebro(object):
    def __init__(self, broker):
        self.datas = list()
        self.strategies = list()
        self.broker = broker(self)

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

    def notify_profit(self, profit):
        for strategy in self.strategies:
            strategy.notify_profit(profit)

    def analyze(self):
        results = Analyzer(self.broker.store.values).results()
        results['value'] = self.broker.value
        results['init_cash'] = self.broker.init_cash
        results['profit'] = self.broker.value - self.broker.init_cash
        results['buy_signal'] = self.broker.store.trades.loc[(self.broker.store.trades['flag'] == Order.Open) & (self.broker.store.trades['side'] == Order.Buy)].shape[0]
        results['sell_signal'] = self.broker.store.trades.loc[(self.broker.store.trades['flag'] == Order.Open) & (self.broker.store.trades['side'] == Order.Sell)].shape[0]
        results['trades'] = self.broker.store.trades.to_dict(orient='records')
        return results

    def run(self):
        self.index = self.datas[0].iloc[0].datetime
        for row in self.datas[0].itertuples():
            self.index = row.datetime
            for strategy in self.strategies:
                strategy.next()
            self.broker.settlement()
        return self.analyze()
