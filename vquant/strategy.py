from vquant.utils import Params
from vquant.broker import Order, Position


class Strategy(object):
    params = tuple()

    def __init__(self, cerebro):
        self.cerebro = cerebro
        self.datas = cerebro.datas

    @property
    def p(self):
        return Params(self.params)

    @property
    def index(self):
        return self.cerebro.index

    @property
    def broker(self):
        return self.cerebro.broker

    @property
    def price(self):
        return self.datas[0].loc[self.index].close

    @property
    def datetime(self):
        return self.datas[0].loc[self.index].datetime

    def position(self, symbol, direction):
        return self.broker.positions(symbol, direction)

    def buy(self, symbol, volume):
        return self.broker.create_order(self.datetime, symbol, Order.Open, Order.Buy, self.price, volume)

    def sell(self, symbol, volume):
        return self.broker.create_order(self.datetime, symbol, Order.Open, Order.Sell, self.price, volume)

    def close(self, symbol, direction, volume):
        side = Order.Sell if direction == Position.Long else Order.Buy
        return self.broker.create_order(self.datetime, symbol, Order.Close, side, self.price, volume)

    def log(self, txt):
        pass

    def notify_order(self, order):
        pass

    def notify_trade(self, trade):
        pass

    def notify_profit(self, profit):
        pass

    def next(self):
        raise NotImplemented

