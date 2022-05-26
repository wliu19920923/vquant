import os
import pandas
import binascii


class BackBroker(object):
    class Order:
        class Side:
            Buy, Sell = ('Buy', 'Sell')

        class Status:
            Created, Partial, Completed, Canceled, Expired, Rejected = ('Created', 'Partial', 'Completed', 'Canceled', 'Expired', 'Rejected')

        Store = pandas.DataFrame(columns=['_id', 'datetime', 'symbol', 'side', 'price', 'quantity', 'traded_quantity', 'commission', 'margin', 'status'])

        @staticmethod
        def create(datetime, symbol, side, price, quantity, commission, margin, status):
            return pandas.Series(
                index=BackBroker.Order.Store.frame.columns,
                data=[binascii.hexlify(os.urandom(12)).decode(), datetime, symbol, side, price, quantity, 0, commission, margin, status]
            )

        @staticmethod
        def submit(order):
            BackBroker.Order.Store = BackBroker.Order.Store.append(order, ignore_index=True)
            BackBroker.Order.Store.set_index(BackBroker.Order.Store['_id'])

    class Trade(object):
        Store = pandas.DataFrame(columns=['_id', 'datetime', 'order_id', 'symbol', 'side', 'price', 'quantity'])

        @staticmethod
        def create(datetime, order_id, symbol, side, price, quantity):
            return pandas.Series(
                index=BackBroker.Order.Store.frame.columns,
                data=[binascii.hexlify(os.urandom(12)).decode(), datetime, order_id, symbol, side, price, quantity]
            )

        @staticmethod
        def submit(trade):
            BackBroker.Trade.Store = BackBroker.Trade.Store.append(trade, ignore_index=True)
            BackBroker.Trade.Store.set_index(BackBroker.Trade.Store['_id'])

    class Position(object):
        class Direction:
            Long, Short = ('Long', 'Short')

        Store = pandas.DataFrame(columns=['_id', 'symbol', 'direction', 'quantity', 'margin', 'cost'])

        @staticmethod
        def create(symbol, direction, quantity, margin, cost):
            return pandas.Series(
                index=BackBroker.Order.Store.frame.columns,
                data=[symbol + direction, symbol, direction, quantity, margin, cost]
            )

        @staticmethod
        def submit(position):
            BackBroker.Position.Store = BackBroker.Position.Store.append(position, ignore_index=True)
            BackBroker.Position.Store.set_index(['symbol', 'direction'])

    def __init__(self, cerebro, commission_rate=0, volume_multiple=1, leverage=1, cash=1000000):
        self.cerebro = cerebro
        self.commission_rate = commission_rate
        self.volume_multiple = volume_multiple
        self.leverage = leverage
        self.cash = cash
        self.value = cash
        self.init_cash = cash
        self.available = cash
        self.frozen = 0

    def on_value(self, value, benchmark_value):
        self.value = value

    def on_order(self, order):
        self.cerebro.notify_order(order)

    def on_trade(self, trade):
        self.cerebro.notify_trade(trade)

    def on_position(self, position):
        self.cerebro.notify_position(position)

    def on_profit(self, profit):
        self.cerebro.notify_profit(profit)

    def get_last_price(self, symbol):
        pass

    def get_position(self, symbol, direction):
        return self.Position.Store.loc[symbol, direction]

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
        order.status = self.Order.Status.Completed
        order.traded_quantity = order.quantity
        trade = self.Trade.create(order.datetime, order.id, order.symbol, order.side, order.price, order.traded_quantity)
        self.Trade.submit(trade)
        self.on_trade(trade)
        return order

    def submit_order(self, order):
        if self.available > order.commission + order.margin:
            self.available = self.available - order.commission - order.margin
            self.frozen = self.frozen + order.margin
            order = self.match_order(order)
        else:
            order.status = self.Order.Status.Rejected
        self.Order.submit(order)
        self.on_order(order)

    def create_order(self, datetime, symbol, side, price, quantity):
        cost = price * quantity
        margin = cost / self.leverage
        commission = cost * self.commission_rate
        order = self.Order.create(datetime, symbol, side, price, quantity, commission, margin, Order.Status.Created)
        self.submit_order(order)

    def cancel_order(self, order_id):
        pass

    def close_position(self, symbol, side, price, quantity):
        pass

    def on_next(self):
        profit = 0
        positions = self.store.positions.loc[self.store.positions['volume'] > 0]
        for row in positions.itertuples():
            price = self.prices[row.symbol]
            volume_multiple = self.symbols[row.symbol].volume_multiple
            if row.direction == self.Position.Direction.Long:
                profit += (price - row.cost / volume_multiple / row.volume) * row.volume * volume_multiple
            else:
                profit += (row.cost / volume_multiple / row.volume - price) * row.volume * volume_multiple
        value = self.available + self.frozen + profit
        benchmark_value = 0
        for symbol in self.symbols:
            benchmark_value += self.prices[symbol] * self.symbols[symbol].volume_multiple
        self.on_value(value, benchmark_value)


__all__ = [BackBroker, ]
