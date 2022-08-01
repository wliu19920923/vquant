from vquant.feeds import DateFeed
from vquant.strategy import Strategy
from vquant.indicators import Indicator


class CrossStrategy(Strategy):
    params = (
        ('symbol', 'J0'),
    )

    def __init__(self, broker, datafeed):
        super(CrossStrategy, self).__init__(broker, datafeed)

    def notify_order(self, order):
        # print(order)
        pass

    def notify_trade(self, trade):
        # print(trade)
        pass

    def notify_profit(self, profit):
        # print(profit)
        pass

    def notify_position(self, position):
        # print(position)
        pass

    def notify_value(self, value):
        # print(value)
        pass

    def next(self):
        dateline = self.dataline[self.params.symbol][self.interval]
        indicator = Indicator(dateline)
        indicator.ma(7)
        indicator.ma(30)
        datanode = indicator.data.loc[self.datetime]
        if datanode.ma7 > datanode.ma30:
            self.buy(self.params.symbol, 1)
        elif datanode.ma7 < datanode.ma30:
            self.sell(self.params.symbol, 1)


if __name__ == '__main__':
    import pandas
    from datetime import timedelta
    from vquant.brokers import BackBroker
    from vquant.analyzer import Analyzer

    datafeed = DateFeed()
    datafeed.read_csv('../datas/J0_day.csv', 'J0', timedelta(days=1))
    datafeed.interval = timedelta(days=1)
    datafeed.datetime = pandas.Timestamp(year=2006, month=1, day=2)
    datafeed.deadline = pandas.Timestamp(year=2006, month=12, day=29)
    strategy = CrossStrategy(broker=BackBroker, datafeed=datafeed)
    symbol_info = strategy.broker.ExchangeInfo.create(symbol='J0', commission_rate=0.0003, leverage=9, quantity_multiple=100, price_tick=0.01, min_quantity=1, min_notional=1)
    strategy.broker.ExchangeInfo.submit(symbol_info)
    strategy.set_cash(1000000)
    strategy.run()
    r = Analyzer(strategy.broker).run()
    print(r)
