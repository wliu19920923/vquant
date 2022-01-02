from vquant.order import Order
from position import Position
from store import Store


class Broker(object):
    """
        - stock_like: 是否是股票
        - commission_rate: 佣金费率
        - margin_rate: 保证金率
        - leverage: 杠杠倍数
        - slide: 价格滑点
        - cash: 现金
        - available: 可以资金
        - frozen: 冻结资金
        - commission_frozen: 手续费冻结
        - margin_use: 保证金占用
        - total_commission: 累计手续费
        - total_profit: 累计盈利
    """

    def __init__(self, cerebro, stock_like=True):
        self.cerebro = cerebro
        self.stock_like = stock_like
        self.commission = 0
        self.margin_rate = 0
        self.slide = 0
        self.cash = 10000
        self.init_cash = self.cash
        self.available = self.cash
        self.frozen = 0
        self.commission_frozen = 0
        self.margin_use = 0
        self.total_commission = 0
        self.total_profit = 0
        self.running = False
        self.store = Store()
        self.order = Order(self)
        self.position = Position(self)

    def set_cash(self, value):
        self.cash = value
        self.init_cash = value
        self.available = value

    def on_order(self, order):
        self.store.update_or_insert_order(order)

    def on_trade(self, trade):
        self.store.insert_trade(trade)
        self.position.on_trade(trade)

    def on_position(self, position):
        self.store.update_or_insert_position(position)

    def orders(self):
        return self.store.active_orders()

    def positions(self, symbol, direction):
        return self.store.query_position(symbol, direction)

    def buy(self, volume):
        return self.order.create(Order.Open, Order.Buy, Order.Market, self.cerebro.price, volume)

    def sell(self, volume):
        return self.order.create(Order.Open, Order.Sell, Order.Market, self.cerebro.price, volume)

    def buy_limit(self, price, volume):
        return self.order.create(Order.Open, Order.Buy, Order.Limit, price, volume)

    def sell_limit(self, price, volume):
        return self.order.create(Order.Open, Order.Sell, Order.Limit, price, volume)

    def cancel(self, order):
        return self.order.cancel(order)

    def close(self, volume, direction):
        side = Order.Sell if direction == Position.Long else Order.Buy
        return self.order.create(Order.Close, side, Order.Market, self.cerebro.price, volume)
