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

    def on_tick(self, ticks):
        for symbol, tick in ticks.items():
            if symbol not in self.dataline:
                self.dataline[symbol] = pandas.DataFrame()
            self.dataline[symbol] = self.dataline[symbol].append(tick)
            self.dataline[symbol].set_index(self.dataline[symbol]['datetime'], inplace=True)
        self.next()

    def on_event(self, evnet, message):
        return getattr(self, evnet)(message)

    def set_cash(self, value):
        self.broker.available = value
        self.broker.frozen = 0

    def set_interval(self, interval):
        self.datafeed.interval = interval

    def set_datetime(self, datetime):
        self.datafeed.datetime = datetime

    def notify_order(self, order):
        raise NotImplemented

    def notify_position(self, position):
        raise NotImplemented

    def notify_trade(self, trade):
        raise NotImplemented

    def next(self):
        raise NotImplemented

    def sell(self, symbol, quantity):
        price = self.dataline[symbol].loc[self.datafeed.datetime].close
        self.broker.create_order(self.datafeed.datetime, symbol, self.broker.Order.Direction.Short, self.broker.Order.Side.Sell, price, quantity)

    def buy(self, symbol, quantity):
        price = self.dataline[symbol].loc[self.datafeed.datetime].close
        self.broker.create_order(self.datafeed.datetime, symbol, self.broker.Order.Direction.Long, self.broker.Order.Side.Buy, price, quantity)

    def run(self):
        self.datafeed.feed_to(self.on_tick)
