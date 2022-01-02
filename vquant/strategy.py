from vquant.param import Param


class Strategy(object):
    def __init__(self, cerebro):
        self.cerebro = cerebro
        if hasattr(self, 'params'):
            self.param = Param(self.params)

    @property
    def datas(self):
        return self.cerebro.datas

    @property
    def broker(self):
        return self.cerebro.broker

    def log(self, txt):
        pass

    def buy(self, volume):
        return self.broker.buy(volume)

    def buy_limit(self, price, volume):
        return self.broker.buy_limit(price, volume)

    def sell(self, volume):
        return self.broker.sell(volume)

    def sell_limit(self, price, volume):
        return self.broker.sell_limit(price, volume)

    def notify_order(self, order):
        '''
        Receives an order whenever there has been a change in one
        '''
        pass

    def notify_trade(self, trade):
        '''
        Receives a trade whenever there has been a change in one
        '''
        pass

    def next(self):
        raise NotImplemented
