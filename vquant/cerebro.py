class Cerebro(object):
    def __init__(self, broker, datafeed, strategy):
        self.broker = broker(self)
        self.datafeed = datafeed
        self.strategy = strategy

    @property
    def datetime(self):
        return self.datafeed.datetime

    def notify_order(self, order):
        self.strategy.notify_order(order)

    def notify_trade(self, trade):
        self.strategy.notify_trade(trade)

    def notify_position(self, position):
        self.strategy.notify_position(position)

    def notify_profit(self, profit):
        self.strategy.notify_profit(profit)

    def on_tick(self):
        self.strategy.next()
        self.broker.on_next()

    def run(self):
        self.datafeed.push(self.on_tick)
