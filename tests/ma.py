from vquant.broker import SymbolInfo, Position
from vquant.strategy import Strategy
from vquant.indicators import Indicator


class MAStrategy(Strategy):
    def __init__(self, cerebro):
        super(MAStrategy, self).__init__(cerebro)
        self.datas[0] = Indicator(self.datas[0]).ma(7)
        self.datas[0] = Indicator(self.datas[0]).ma(30)

    # def notify_order(self, order):
    #     print(order.__dict__())
    #
    # def notify_trade(self, trade):
    #     print(trade.__dict__())
    #
    # def notify_profit(self, profit):
    #     print(profit.__dict__())

    def next(self):
        # print(self.datas[0][:self.index])
        print(self.datas[0].iloc[-20:])
        ma7 = self.datas[0].loc[self.index].ma7
        ma30 = self.datas[0].loc[self.index].ma30
        long_position = self.position('a2201', Position.Long)
        if long_position.volume:
            if ma7 > ma30:
                return
            self.close('a2201', Position.Long, long_position.volume)
        else:
            if ma7 > ma30:
                self.buy('a2201', 1)
        short_position = self.position('a2201', Position.Short)
        if short_position.volume:
            if ma7 < ma30:
                return
            self.close('a2201', Position.Short, short_position.volume)
        else:
            if ma7 < ma30:
                self.sell('a2201', 1)


if __name__ == '__main__':
    from vquant.cerebro import Cerebro
    from vquant.broker.backbroker import BackBroker
    from vquant.feeds.csvread import CSVRead

    cerebro = Cerebro(broker=BackBroker)
    symbol_info = SymbolInfo(5, 0.2, 5, 0)
    cerebro.broker.add_symbol('a2201', symbol_info)
    cerebro.broker.set_cash(1000000)
    data = CSVRead('../datas/2006day1.csv').data
    cerebro.add_data(data)
    cerebro.add_strategy(MAStrategy)
    r = cerebro.run()
    print(r)
