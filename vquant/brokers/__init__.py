import os
import binascii
from dateutil.parser import parse
from vquant.stores import Store


class Order(object):
    """
      Order Flags
      - Open: increase position
      - Close: reduce position
      Order Types
      - Buy: buy
      - Sell: Sell
      Order Status
      - Submitted: sent to the brokers and awaiting confirmation
      - Accepted: accepted by the brokers
      - Partial: partially executed
      - Completed: fully executed
      - Canceled/Cancelled: canceled by the user
      - Expired: expired
      - Margin: not enough cash to execute the order.
      - Rejected: Rejected by the brokers
    """

    class Flag:
        Open, Close, CloseToday, CloseYesterday = ('Open', 'Close', 'CloseToday', 'CloseYesterday')

    class Side:
        Buy, Sell = ('Buy', 'Sell')

    class Status:
        Created, Submitted, Accepted, Partial, Completed, Canceled, Expired, Margin, Rejected = (
            'Created', 'Submitted', 'Accepted', 'Partial', 'Completed',
            'Canceled', 'Expired', 'Margin', 'Rejected'
        )

    def __init__(self, _datetime, symbol, flag, side, price, quantity, commission, margin, status):
        self._id = binascii.hexlify(os.urandom(12)).decode()
        self._datetime = _datetime
        self.symbol = symbol
        self.flag = flag
        self.side = side
        self.price = price
        self.quantity = quantity
        self.commission = commission
        self.margin = margin
        self.status = status


class Trade(object):
    def __init__(self, _datetime, order_id, symbol, flag, side, price, quantity, profit):
        self._id = binascii.hexlify(os.urandom(12)).decode()
        self._datetime = _datetime
        self.order_id = order_id
        self.symbol = symbol
        self.flag = flag
        self.side = side
        self.price = price
        self.quantity = quantity
        self.profit = profit


class Position(object):
    class Direction:
        Long, Short = ('Long', 'Short')

    def __init__(self, symbol, cost, direction, volume, margin):
        self.symbol = symbol
        self.cost = cost
        self.direction = direction
        self.volume = volume
        self.margin = margin


class Profit(object):
    def __init__(self, _datetime, amount):
        self._datetime = _datetime
        self.amount = amount


class SymbolInfo(object):
    """
        - commission_rate: 每笔手续费
        - margin_rate: 保证金率
        - volume_multiple: 数量乘数
        - price_tick: 最小波动价格
        - exchange_id: 交易所编号
        - target_index: 数据下标
        - prompt_day: 交割日
    """

    def __init__(self, commission_rate, margin_rate, volume_multiple, price_tick, exchange_id, target_index, prompt_day=None):
        self.commission_rate = commission_rate
        self.margin_rate = margin_rate
        self.volume_multiple = volume_multiple
        self.price_tick = price_tick
        self.exchange_id = exchange_id
        self.target_index = target_index
        self.prompt_day = prompt_day


class BackBroker(object):
    def __init__(self, cerebro, **kwargs):
        self.cerebro = cerebro
        self.commission_rate = kwargs.get('commission_rate') or 0
        self.margin_rate = kwargs.get('margin_rate') or 0
        self.cash = kwargs.get('cash') or 1000000
        self.value = self.cash
        self.init_cash = self.cash
        self.available = self.cash
        self.frozen = 0

    @property
    def prices(self):
        return {symbol: self.cerebro.datas[self.symbols[symbol].target_index].loc[self.cerebro.index].close for symbol in self.symbols}

    @property
    def current_trading_day(self):
        return parse(self.cerebro.index).day

    def previous_trading_day(self, target_index):
        data = self.cerebro.datas[target_index].loc[:self.cerebro.index]
        return parse(data.iloc[-2].datetime).day

    def on_value(self, value, benchmark_value):
        self.value = value
        self.store.insert_value(dict(datetime=self.cerebro.datetime, value=value, benchmark_value=benchmark_value))

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
        return self.store.query_orders(symbol, side, [Order.Created, Order.Submitted, Order.Accepted, Order.Partial])

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
        if order.flag == order.Open:
            self.frozen += order.margin
            self.available -= order.margin
        order.status = order.Accepted
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
        order.status = order.Completed
        self.on_order(order)
        trade = Trade(order.datetime, order.id, order.symbol, order.flag, order.side, order.price, order.volume, 0)
        if trade.flag == order.Open:
            trade = self.opening(trade)
        else:
            trade = self.closing(trade)
        self.on_trade(trade)
        return order

    def submit_order(self, order):
        order.status = order.Submitted
        if not self.check_order_cash_use(order):
            order.status = order.Margin
            self.on_order(order)
            return
        order = self.deduction_deposit(order)
        self.on_order(order)
        self.match_order(order)

    def create_order(self, dt, symbol, flag, side, price, volume):
        cost = price * volume * self.symbols[symbol].volume_multiple
        margin = cost * self.symbols[symbol].margin_rate if flag == Order.Open else 0
        commission = cost * self.symbols[symbol].commission_rate
        order = Order(dt, symbol, flag, side, price, volume, commission, margin, Order.Created)
        self.submit_order(order)

    def on_next(self):
        profit = 0
        positions = self.store.positions.loc[self.store.positions['volume'] > 0]
        for row in positions.itertuples():
            price = self.prices[row.symbol]
            volume_multiple = self.symbols[row.symbol].volume_multiple
            if row.direction == Position.Long:
                profit += (price - row.cost / volume_multiple / row.volume) * row.volume * volume_multiple
            else:
                profit += (row.cost / volume_multiple / row.volume - price) * row.volume * volume_multiple
        value = self.available + self.frozen + profit
        benchmark_value = 0
        for symbol in self.symbols:
            benchmark_value += self.prices[symbol] * self.symbols[symbol].volume_multiple
        self.on_value(value, benchmark_value)
