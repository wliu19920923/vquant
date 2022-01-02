import os
import binascii
from vquant.order import Order


class Matcher(object):
    def __init__(self, broker, order):
        self.order = order
        self.broker = broker

    @property
    def is_limit_order(self):
        return self.order['type'] == Order.Limit

    @property
    def price_slide(self):
        return self.broker.slide if self.order['side'] == Order.Buy else - self.broker.slide

    @property
    def trade_id(self):
        return binascii.hexlify(os.urandom(12)).decode()

    def create_trade_record(self):
        return dict(trade_id=self.trade_id, order_id=self.order['order_id'], )

    def limit_trading(self):
        self.order['deal_price'] = self.order['price']
        self.order['status'] = Order.Completed
        self.broker.on_order(self.order)
        trade_record = self.create_trade_record()
        self.broker.on_trade(trade_record)

    def market_trading(self):
        self.order['deal_price'] = self.broker.cerebro.price + self.price_slide
        self.order['status'] = Order.Completed
        self.broker.on_order(self.order)
        trade_record = self.create_trade_record()
        self.broker.on_trade(trade_record)

    def exec(self):
        if self.is_limit_order:
            if self.broker.cerebro.price == self.order['price']:
                self.limit_trading()
        else:
            self.market_trading()
        return self.order
