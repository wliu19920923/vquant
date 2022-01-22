import os
import binascii
from datetime import datetime
from vquant.stores import Store


class Profit(object):
    def __init__(self, dt, amount):
        self.datetime = dt
        self.amount = amount

    def __dict__(self):
        return {
            'datetime': self.datetime,
            'amount': self.amount
        }


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
        Open, Close, CloseToday, CloseYesterday = range(4)
        Flags = ['Open', 'Close', 'CloseToday', 'CloseYesterday']

        Buy, Sell = range(2)
        Sides = ['Buy', 'Sell']

        Created, Submitted, Accepted, Partial, Completed, Canceled, Expired, Margin, Rejected = range(9)
        Status = [
            'Created', 'Submitted', 'Accepted', 'Partial', 'Completed',
            'Canceled', 'Expired', 'Margin', 'Rejected'
        ]

        def __init__(self, dt, symbol, flag, side, price, volume, commission, margin, status):
            self.id = binascii.hexlify(os.urandom(12)).decode()
            self.datetime = dt
            self.symbol = symbol
            self.flag = flag
            self.side = side
            self.price = price
            self.volume = volume
            self.commission = commission
            self.margin = margin
            self.status = status

        def __dict__(self):
            return {
                'id': self.id,
                'datetime': self.datetime,
                'symbol': self.symbol,
                'flag': self.flag,
                'side': self.side,
                'price': self.price,
                'volume': self.volume,
                'commission': self.commission,
                'margin': self.margin,
                'status': self.status
            }

    class Trade(object):
        def __init__(self, dt, order_id, symbol, flag, side, price, volume, profit):
            self.id = binascii.hexlify(os.urandom(12)).decode()
            self.datetime = dt
            self.order_id = order_id
            self.symbol = symbol
            self.flag = flag
            self.side = side
            self.price = price
            self.volume = volume
            self.profit = profit

        def __dict__(self):
            return {
                'id': self.id,
                'datetime': self.datetime,
                'order_id': self.order_id,
                'symbol': self.symbol,
                'flag': self.flag,
                'side': self.side,
                'price': self.price,
                'volume': self.volume,
                'profit': self.profit
            }

    class Position(object):
        Long, Short = range(2)
        Directions = ['Long', 'Short']

        def __init__(self, symbol, cost, direction, volume, margin):
            self.symbol = symbol
            self.cost = cost
            self.direction = direction
            self.volume = volume
            self.margin = margin

        def __dict__(self):
            return {
                'symbol': self.symbol,
                'cost': self.cost,
                'direction': self.direction,
                'volume': self.volume,
                'margin': self.margin,
            }

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

    @property
    def prices(self):
        return {symbol: self.cerebro.datas[self.symbols[symbol].target_index].loc[self.cerebro.index].close for symbol in self.symbols}

    def previous_trading_day(self, target_index):
        data = self.cerebro.datas[target_index].loc[:self.cerebro.index]
        return datetime.strptime(data.iloc[-2].datetime, '%Y-%m-%d %H:%M:%S').day

    @property
    def current_trading_day(self):
        return datetime.strptime(self.cerebro.index, '%Y-%m-%d %H:%M:%S').day

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
        return self.store.query_orders(symbol, side, [self.Order.Created, self.Order.Submitted, self.Order.Accepted, self.Order.Partial])

    def positions(self, symbol, direction):
        pandas_data = self.store.query_position(symbol, direction)
        if not len(pandas_data.index):
            return self.Position(symbol, 0, direction, 0, 0)
        record = pandas_data.iloc[0]
        return self.Position(record.symbol, record.cost, record.direction, record.volume, record.margin)

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
        if trade.side == self.Order.Buy:
            position = self.positions(trade.symbol, self.Position.Long)
        else:
            position = self.positions(trade.symbol, self.Position.Short)
        cost = trade.price * trade.volume * self.symbols[trade.symbol].volume_multiple
        position.cost += cost
        position.margin += cost * self.symbols[trade.symbol].margin_rate
        position.volume += trade.volume
        self.on_position(position)
        return trade

    def closing(self, trade):
        if trade.side == self.Order.Buy:
            position = self.positions(trade.symbol, self.Position.Short)
            trade.profit = (position.cost / position.volume - trade.price) * trade.volume
        else:
            position = self.positions(trade.symbol, self.Position.Long)
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
        trade = self.Trade(order.datetime, order.id, order.symbol, order.flag, order.side, order.price, order.volume, 0)
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
        margin = cost * self.symbols[symbol].margin_rate if flag == self.Order.Open else 0
        commission = cost * self.symbols[symbol].commission_rate
        order = self.Order(dt, symbol, flag, side, price, volume, commission, margin, self.Order.Created)
        self.submit_order(order)

    def move_positions(self):
        positions = self.store.positions.loc[self.store.positions['volume'] > 0]
        for row in positions.itertuples():
            info = self.symbols[row.symbol]
            if info.prompt_day == self.current_trading_day and self.previous_trading_day(info.target_index) != info.prompt_day:
                if row.direction == self.Position.Long:
                    self.create_order(self.cerebro.index, row.symbol, self.Order.Close, self.Order.Sell, self.prices[row.symbol], row.volume)
                    self.create_order(self.cerebro.index, row.symbol, self.Order.Open, self.Order.Buy, self.prices[row.symbol], row.volume)
                else:
                    self.create_order(self.cerebro.index, row.symbol, self.Order.Close, self.Order.Buy, self.prices[row.symbol], row.volume)
                    self.create_order(self.cerebro.index, row.symbol, self.Order.Open, self.Order.Sell, self.prices[row.symbol], row.volume)

    def settlement(self):
        profit = 0
        self.move_positions()
        positions = self.store.positions.loc[self.store.positions['volume'] > 0]
        for row in positions.itertuples():
            price = self.prices[row.symbol]
            volume_multiple = self.symbols[row.symbol].volume_multiple
            if row.direction == self.Position.Long:
                profit += (price - row.cost / volume_multiple / row.volume) * row.volume * volume_multiple
            else:
                profit += (row.cost / volume_multiple / row.volume - price) * row.volume * volume_multiple
        value = self.available + self.frozen + profit
        benchmark_value = 0
        for symbol in self.symbols:
            benchmark_value += self.prices[symbol] * self.symbols[symbol].volume_multiple
        self.on_value(value, benchmark_value)
