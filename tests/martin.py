from vquant.brokers import SymbolInfo
from vquant.strategy import Strategy
from vquant.indicators import Indicator


class Martin(Strategy):
    _params = (
        ('symbol', 'btc_usdt'),
    )

    def __init__(self, cerebro):
        super().__init__(cerebro)

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

