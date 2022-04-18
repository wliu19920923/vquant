from vquant.brokers import SymbolInfo
from vquant.strategy import Strategy
from vquant.indicators import Indicator


class CrossStrategy(Strategy):
    _params = (
        ('symbol', 'j0'),
    )

    def __init__(self, cerebro):
        super(CrossStrategy, self).__init__(cerebro)
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
        bar = self.datas[0].loc[self.index]
        long_position = self.get_position(self.params.symbol, self.broker.Position.Long)
        if long_position.volume:
            if bar.ma7 > bar.ma30:
                return
            self.close(self.params.symbol, self.broker.Position.Long, long_position.volume)
        else:
            if bar.ma7 > bar.ma30:
                self.buy(self.params.symbol, 1)
        short_position = self.get_position(self.params.symbol, self.broker.Position.Short)
        if short_position.volume:
            if bar.ma7 < bar.ma30:
                return
            self.close(self.params.symbol, self.cerebro.broker.Position.Short, short_position.volume)
        else:
            if bar.ma7 < bar.ma30:
                self.sell(self.params.symbol, 1)


if __name__ == '__main__':
    from vquant.cerebro import Cerebro
    from vquant.brokers import BackBroker
    from vquant.feeds.readcsv import ReadCSV

    cerebro = Cerebro(broker=BackBroker)
    symbol_info = SymbolInfo(commission_rate=0.0003, margin_rate=0.09, volume_multiple=100, price_tick=0.01, exchange_id='BackBroker', target_index=0)
    cerebro.broker.add_symbol('j0', symbol_info)
    cerebro.broker.set_cash(1000000)
    data = ReadCSV('../datas/2006day1.csv').data
    cerebro.add_data(data)
    cerebro.add_strategy(CrossStrategy)
    analyzer = cerebro.run()
    print(analyzer.results)
