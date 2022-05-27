import os
import pandas
import binascii


class BackBroker(object):
    class Order:
        class Side:
            Buy, Sell = ('Buy', 'Sell')

        class Status:
            Created, Partial, Completed, Canceled, Expired, Rejected = ('Created', 'Partial', 'Completed', 'Canceled', 'Expired', 'Rejected')

        class Direction:
            Long, Short = ('Long', 'Short')

        Store = pandas.DataFrame(columns=['_id', 'datetime', 'symbol', 'direction', 'side', 'price', 'quantity', 'traded_quantity', 'commission', 'margin', 'status'])

        @staticmethod
        def create(datetime, symbol, direction, side, price, quantity, commission, margin, status):
            return pandas.Series(
                index=BackBroker.Order.Store.frame.columns,
                data=[binascii.hexlify(os.urandom(12)).decode(), datetime, symbol, direction, side, price, quantity, 0, commission, margin, status]
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
            BackBroker.Position.Store.set_index(BackBroker.Position.Store['_id'])

    class ExchangeInfo(object):
        Store = pandas.DataFrame(columns=['symbol', 'commission_rate', 'leverage', 'price_tick', 'quantity_multiple', 'min_quantity', 'min_notional'])

        @staticmethod
        def create(symbol, commission_rate, leverage, price_tick, quantity_multiple, min_quantity, min_notional):
            return pandas.Series(
                index=BackBroker.Order.Store.frame.columns,
                data=[symbol, commission_rate, leverage, price_tick, quantity_multiple, min_quantity, min_notional]
            )

        @staticmethod
        def submit(info):
            BackBroker.ExchangeInfo.Store = BackBroker.ExchangeInfo.Store.append(info, ignore_index=True)
            BackBroker.ExchangeInfo.Store.set_index(BackBroker.ExchangeInfo.Store['symbol'])

    def __init__(self, callback):
        self.datetime = pandas.Timestamp.now()
        self.callback = callback
        self.available = 1000000
        self.frozen = 0

    def on_tick(self, datetime):
        self.datetime = datetime

    def on_order(self, order):
        self.callback('notify_order', order)

    def on_trade(self, trade):
        self.callback('notify_trade', trade)

    def on_position(self, position):
        self.callback('notify_position', position)

    def on_profit(self, profit):
        self.callback('notify_profit', profit)

    def get_position(self, symbol, direction):
        return self.Position.Store.loc[symbol + direction]

    def close_order(self, order):
        if order.direction == self.Order.Direction.Long and order.side == self.Order.Side.Sell:
            position = self.Position.Store.loc[order.symbol + self.Order.Direction.Long]
            avg_price = position.cost / position.quantity
            self.available += (order.price - avg_price) * order.quantity
            position.quantity = position.quantity - order.quantity
            position.cost = position.cost - avg_price * order.quantity
        elif order.direction == self.Order.Direction.Short and order.side == self.Order.Side.Buy:
            position = self.Position.Store.loc[order.symbol + self.Order.Direction.Short]
            avg_price = position.cost / position.quantity
            self.available += (avg_price - order.price) * order.quantity
            position.quantity = position.quantity - order.quantity
            position.cost = position.cost - avg_price * order.quantity
        return order

    def settle_order(self, order):
        order.status = self.Order.Status.Completed
        order.traded_quantity = order.quantity
        self.available = self.available - order.commission - order.margin
        self.frozen = self.frozen + order.margin
        return order

    def match_order(self, order):
        order = self.settle_order(order)
        trade = self.Trade.create(order.datetime, order.id, order.symbol, order.side, order.price, order.traded_quantity)
        self.Trade.submit(trade)
        self.on_trade(trade)
        return order

    def submit_order(self, order):
        if self.available > order.commission + order.margin:
            order = self.match_order(order)
        else:
            order.status = self.Order.Status.Rejected
        self.Order.submit(order)
        self.on_order(order)

    def create_order(self, symbol, direction, side, price, quantity):
        cost = price * quantity
        info = self.ExchangeInfo.Store.loc[symbol]
        margin = cost / info.leverage
        commission = cost * info.commission_rate
        order = self.Order.create(self.datetime, symbol, direction, side, price, quantity, commission, margin, self.Order.Status.Created)
        self.submit_order(order)

    def cancel_order(self, symbol, order_id):
        raise NotImplemented

    def close_long_position(self, symbol, price, quantity):
        cost = price * quantity
        info = self.ExchangeInfo.Store.loc[symbol]
        position = self.Position.Store.loc[symbol + self.Order.Direction.Long]
        commission = cost * info.commission_rate
        margin = -(position.margin / position.quantity * quantity)
        order = self.Order.create(self.datetime, symbol, self.Order.Direction.Long, self.Order.Side.Sell, price, quantity, commission, margin, self.Order.Status.Created)
        self.submit_order(order)

    def close_short_position(self, symbol, price, quantity):
        cost = price * quantity
        info = self.ExchangeInfo.Store.loc[symbol]
        position = self.Position.Store.loc[symbol + self.Order.Direction.Short]
        commission = cost * info.commission_rate
        margin = -(position.margin / position.quantity * quantity)
        order = self.Order.create(self.datetime, symbol, self.Order.Direction.Short, self.Order.Side.Buy, price, quantity, commission, margin, self.Order.Status.Created)
        self.submit_order(order)


__all__ = [BackBroker, ]
