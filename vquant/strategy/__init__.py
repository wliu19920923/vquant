import pandas
from vquant.strategy.params import Params


class Strategy(object):
    params = tuple()

    def __init__(self, broker, datafeed):
        self.broker = broker(self.on_event)
        self.datafeed = datafeed
        self.dataline = dict()
        self.params = Params(self.params)

    def log(self, txt):
        raise NotImplemented

    @property
    def order(self):
        return self.broker.Order.Store

    @property
    def trade(self):
        return self.broker.Trade.Store

    @property
    def datetime(self):
        return self.datafeed.datetime

    @property
    def interval(self):
        return self.datafeed.interval

    @property
    def netvalue(self):
        return self.broker.NetValue.Store

    @property
    def position(self):
        return self.broker.Position.Store

    def notify_order(self, order):
        raise NotImplemented

    def notify_position(self, position):
        raise NotImplemented

    def notify_trade(self, trade):
        raise NotImplemented

    def notify_value(self, value):
        raise NotImplemented

    def set_cash(self, value):
        self.broker.available = value
        self.broker.frozen = 0

    def on_event(self, evnet, message):
        return getattr(self, evnet)(message)

    def on_tick(self, ticks):
        for symbol, tick in ticks.items():
            if symbol not in self.dataline:
                self.dataline[symbol] = dict()
            for interval in tick:
                if interval not in self.dataline[symbol]:
                    self.dataline[symbol][interval] = pandas.DataFrame()
                self.dataline[symbol][interval] = self.dataline[symbol][interval].append(tick[interval])
                self.dataline[symbol][interval].set_index(self.dataline[symbol][interval]['datetime'], inplace=True)
        self.broker.datetime = self.datetime
        self.on_next()

    def on_next(self):
        self.next()
        benchmark_value, value = 0, self.broker.available + self.broker.frozen
        for symbol in self.dataline:
            initial_price = self.dataline[symbol][self.interval].iloc[0].close
            price = self.dataline[symbol][self.interval].loc[self.datetime].close
            benchmark_value += price - initial_price
            position = self.broker.Position.Store.loc[symbol]
            value = value + price * position.quantity - position.cost
        netvalue = self.broker.NetValue.create(self.datetime, benchmark_value, value)
        self.broker.NetValue.submit(netvalue)
        self.broker.on_value(netvalue)

    def next(self):
        raise NotImplemented

    def sell(self, symbol, quantity):
        price = self.dataline[symbol][self.interval].loc[self.datetime].close
        self.broker.create_order(symbol, self.broker.Order.Side.Sell, price, quantity)

    def buy(self, symbol, quantity):
        price = self.dataline[symbol][self.interval].loc[self.datetime].close
        self.broker.create_order(symbol, self.broker.Order.Side.Buy, price, quantity)

    def run(self):
        self.datafeed.feed_to(self.on_tick)
