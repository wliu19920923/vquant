class Params(object):
    def __init__(self, params: tuple):
        for key, value in params:
            setattr(self, key, value)


class Strategy(object):
    _params = tuple()

    def __init__(self, cerebro):
        self.cerebro = cerebro
        self.datas = cerebro.datas
        self.params = Params(self._params)

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

    def get_position(self, symbol, direction):
        return self.broker.positions(symbol, direction)

    def buy(self, symbol, volume):
        return self.broker.create_order(self.datetime, symbol, self.broker.Order.Open, self.broker.Order.Buy, self.price, volume)

    def sell(self, symbol, volume):
        return self.broker.create_order(self.datetime, symbol, self.broker.Order.Open, self.broker.Order.Sell, self.price, volume)

    def close(self, symbol, direction, volume):
        side = self.broker.Order.Sell if direction == self.broker.Position.Long else self.broker.Order.Buy
        return self.broker.create_order(self.datetime, symbol, self.broker.Order.Close, side, self.price, volume)

    def close_today(self, symbol, direction, volume):
        side = self.broker.Order.Sell if direction == self.broker.Position.Long else self.broker.Order.Buy
        return self.broker.create_order(self.datetime, symbol, self.broker.Order.CloseToday, side, self.price, volume)

    def close_yesterday(self, symbol, direction, volume):
        side = self.broker.Order.Sell if direction == self.broker.Position.Long else self.broker.Order.Buy
        return self.broker.create_order(self.datetime, symbol, self.broker.Order.CloseYesterday, side, self.price, volume)

    def log(self, txt):
        pass

    def notify_order(self, order):
        pass

    def notify_trade(self, trade):
        pass

    def notify_position(self, position):
        pass

    def notify_profit(self, profit):
        pass

    def next(self):
        raise NotImplemented
