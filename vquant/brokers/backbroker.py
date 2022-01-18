from vquant.brokers import Order, Trade, Position, Profit
from vquant.stores import Store


class BackBroker(object):
    def __init__(self, cerebro):
        self.cerebro = cerebro
        self.slide = 0
        self.cash = 1000000
        self.value = self.cash
        self.init_cash = self.cash
        self.available = self.cash
        self.frozen = 0
        self.symbols = dict()
        self.store = Store()

    def set_cash(self, value):
        self.cash = value
        self.value = value
        self.init_cash = value
        self.available = value
        self.frozen = 0

    def add_symbol(self, symbol, info):
        self.symbols[symbol] = info

    def get_price(self, symbol):
        return self.cerebro.datas[self.symbols[symbol].target_index].loc[self.cerebro.index].close

    def on_value(self, value, benchmark_value):
        self.value = value
        self.store.insert_value(dict(datetime=self.cerebro.index, value=value, benchmark_value=benchmark_value))

    def on_order(self, order):
        self.store.update_or_insert_order(order.__dict__())
        self.cerebro.notify_order(order)

    def on_trade(self, trade):
        self.store.insert_trade(trade.__dict__())
        self.cerebro.notify_trade(trade)

    def on_position(self, position):
        self.store.update_or_insert_position(position.__dict__())

    def on_profit(self, profit):
        self.store.insert_profit(profit.__dict__())
        self.cerebro.notify_profit(profit)

    def orders(self, symbol, side):
        return self.store.query_orders(symbol, side)

    def positions(self, symbol, direction):
        pandas_data = self.store.query_position(symbol, direction)
        if not len(pandas_data.index):
            return Position(symbol, 0, direction, 0, 0)
        record = pandas_data.iloc[0]
        return Position(record.symbol, record.cost, record.direction, record.volume, record.margin)

    def check_order_cash_use(self, order):
        cash_use = order.commission + order.margin
        return self.available > cash_use

    def deduction_deposit(self, order):
        self.available -= order.commission
        if order.flag == Order.Open:
            self.frozen += order.margin
            self.available -= order.margin
        order.status = Order.Accepted
        return order

    def opening(self, trade):
        if trade.side == Order.Buy:
            position = self.positions(trade.symbol, Position.Long)
        else:
            position = self.positions(trade.symbol, Position.Short)
        cost = trade.price * trade.volume * self.symbols[trade.symbol].volume_multiple
        position.cost += cost
        position.margin += cost * self.symbols[trade.symbol].margin_rate
        position.volume += trade.volume
        self.on_position(position)
        return trade

    def closing(self, trade):
        if trade.side == Order.Buy:
            position = self.positions(trade.symbol, Position.Short)
            trade.profit = (position.cost / position.volume - trade.price) * trade.volume
        else:
            position = self.positions(trade.symbol, Position.Long)
            trade.profit = (trade.price - position.cost / position.volume) * trade.volume
        margin = position.margin / position.volume * trade.volume
        position.cost -= position.cost / position.volume * trade.volume
        position.margin -= margin
        position.volume -= trade.volume
        self.on_position(position)
        self.frozen -= margin
        self.available += margin
        self.available += trade.profit
        self.cash += margin + trade.profit
        profit = Profit(self.cerebro.index, trade.profit)
        self.on_profit(profit)
        return trade

    def match_order(self, order):
        order.status = Order.Completed
        self.on_order(order)
        trade = Trade(order.datetime, order.id, order.symbol, order.flag, order.side, order.price, order.volume, 0)
        if trade.flag == Order.Open:
            trade = self.opening(trade)
        else:
            trade = self.closing(trade)
        self.on_trade(trade)
        return order

    def submit_order(self, order):
        order.status = Order.Submitted
        if not self.check_order_cash_use(order):
            order.status = Order.Margin
            self.on_order(order)
            return
        order = self.deduction_deposit(order)
        self.on_order(order)
        self.match_order(order)

    def create_order(self, datetime, symbol, flag, side, price, volume):
        cost = price * volume * self.symbols[symbol].volume_multiple
        margin = cost * self.symbols[symbol].margin_rate if flag == Order.Open else 0
        commission = volume * self.symbols[symbol].commission
        order = Order(datetime, symbol, flag, side, price, volume, commission, margin, Order.Created)
        self.submit_order(order)

    def settlement(self):
        profit = 0
        prices = {symbol: self.get_price(symbol) for symbol in self.symbols}
        for row in self.store.positions.itertuples():
            if row.volume:
                price = prices[row.symbol]
                volume_multiple = self.symbols[row.symbol].volume_multiple
                if row.direction == Position.Long:
                    profit += (price - row.cost / volume_multiple / row.volume) * row.volume * volume_multiple
                else:
                    profit += (row.cost / volume_multiple / row.volume - price) * row.volume * volume_multiple
        value = self.available + self.frozen + profit
        benchmark_value = 0
        for symbol in self.symbols:
            benchmark_value += prices[symbol] * self.symbols[symbol].volume_multiple
        self.on_value(value, benchmark_value)
