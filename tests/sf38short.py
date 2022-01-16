import talib
import numpy
import pandas
from vquant.broker import SymbolInfo, Position
from vquant.strategy import Strategy
from vquant.indicators import Indicator


class SF38ShortStrategy(Strategy):
    params = (
        ('symbol', 'j0'),
        ('multi', 1.25),  # 几倍art止盈
        ('hh_mul', 1.5),  # open range breaker atr倍数
        ('exit_mul', 2),
        ('lots', 2),  # 手数
        ('fast', 2),
        ('slow', 30),
        ('len_c', 50),
        ('len_fast', 5),
        ('len_slow', 25),
        ('length', 20),
    )

    def __init__(self, cerebro):
        super(SF38ShortStrategy, self).__init__(cerebro)
        temp = talib.EMA(self.datas[0].close.values, timeperiod=self.p.len_fast) + talib.EMA(self.datas[0].close.values, timeperiod=self.p.len_slow)
        temp = talib.EMA(temp, timeperiod=self.p.len_c) / 2
        self.datas[0]['c'] = temp.tolist()
        self.datas[0] = Indicator(self.datas[0]).atr()
        self.datas[0]['v1_pre_ma'] = talib.MA((self.datas[0].close - self.datas[0].open).abs().values, timeperiod=self.p.length)
        self.diff = numpy.zeros(20)
        self.trend = numpy.zeros(20)
        self.up_trend = numpy.zeros(20)
        self.down_trend = numpy.zeros(20)
        self.eff_ratio = numpy.zeros(20)
        self.short_exit_price = numpy.zeros(20)

    def update_array(self, arr, value):
        arr[:-1] = arr[1:]
        arr[-1] = value

    def next(self):
        bar = self.datas[0].loc[self.index]
        history_data = self.datas[0].loc[:self.index]
        previous20_data = history_data.iloc[-20:]
        v_max = previous20_data['v1_pre_ma'].max()
        up_lev = bar.c - (self.p.multi * v_max)
        dn_lev = bar.c + (self.p.multi * v_max)

        if bar.close > self.up_trend[-1]:
            self.update_array(self.up_trend, max(up_lev, self.up_trend[-1]))
        else:
            self.update_array(self.up_trend, up_lev)

        if bar.close < self.down_trend[-1]:
            self.update_array(self.down_trend, min(dn_lev, self.down_trend[-1]))
        else:
            self.update_array(self.down_trend, dn_lev)

        if bar.close > self.down_trend[-1]:
            self.update_array(self.trend, 1)
        else:
            # if trend_ready2[1]:
            if bar.close < self.up_trend[-1]:
                self.update_array(self.trend, -1)
            else:
                self.update_array(self.trend, self.trend[-1])

        st_line = self.up_trend[-1] if self.trend[-1] == 1 else self.down_trend[-1]
        hour9_time_index = pandas.Timestamp('%s 09:00:00' % bar.datetime[:10])
        today_open = self.datas[0].loc[hour9_time_index].open if hour9_time_index in self.datas[0].index else 0
        ll = today_open - bar.atr * self.p.hh_mul
        short_position = self.position(self.p.symbol, Position.Short)
        if not short_position.volume and bar.close <= ll and self.trend[-1] == -1 and bar.close <= st_line:
            self.sell(self.p.symbol, self.p.lots)
            self.open_bar = 0  # 开仓历时
        fastest = 2 / (self.p.fast + 1)
        slowest = 2 / (self.p.slow + 1)
        if history_data.shape[0] < 10:
            return
        net_chg = abs(bar.close - history_data.iloc[-10].close)
        self.update_array(self.diff, abs(bar.close - history_data.iloc[-2].close))
        tot_chg = sum(abs(self.diff))
        if tot_chg > 0 and net_chg != 0:
            self.update_array(self.eff_ratio, net_chg / tot_chg)
        else:
            self.update_array(self.eff_ratio, self.eff_ratio[-1])

        if short_position.volume:
            if self.open_bar == 0:
                self.update_array(self.short_exit_price, st_line + bar.atr * self.p.exit_mul)
                self.open_bar += 1
            elif self.open_bar > 0:

                cc = self.eff_ratio[-1] * (fastest - slowest) + slowest
                sc = cc ** 3
                adp_loc = 5 if round(1 / self.eff_ratio[-1]) > 5 else 0
                self.update_array(self.short_exit_price, self.short_exit_price[-1] + sc * (history_data.iloc[-adp_loc].high - self.short_exit_price[-1]))

                if bar.high >= self.short_exit_price[-1]:
                    self.close(self.p.symbol, Position.Short, self.p.lots)


if __name__ == '__main__':
    from vquant.cerebro import Cerebro
    from vquant.broker.backbroker import BackBroker
    from vquant.feeds.csvread import CSVRead

    cerebro = Cerebro(broker=BackBroker)
    symbol_info = SymbolInfo(commission=3, margin_rate=0.09, volume_multiple=100, target_index=0)
    cerebro.broker.add_symbol('j0', symbol_info)
    cerebro.broker.set_cash(1000000)
    data = CSVRead('../datas/J0_30m.csv').data
    cerebro.add_data(data)
    cerebro.add_strategy(SF38ShortStrategy)
    r = cerebro.run()
    print(r)
