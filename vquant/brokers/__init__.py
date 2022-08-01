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
                index=BackBroker.Order.Store.columns,
                data=[binascii.hexlify(os.urandom(12)).decode(), datetime, symbol, side, price, quantity, 0, commission, margin, status]
            )

        @staticmethod
        def submit(order):
            BackBroker.Order.Store = BackBroker.Order.Store.append(order, ignore_index=True)
            BackBroker.Order.Store = BackBroker.Order.Store.set_index(BackBroker.Order.Store['_id'])

    class Trade(object):
        Store = pandas.DataFrame(columns=['_id', 'datetime', 'order_id', 'symbol', 'side', 'price', 'quantity'])

        @staticmethod
        def create(datetime, order_id, symbol, side, price, quantity):
            return pandas.Series(
                index=BackBroker.Trade.Store.columns,
                data=[binascii.hexlify(os.urandom(12)).decode(), datetime, order_id, symbol, side, price, quantity]
            )

        @staticmethod
        def submit(trade):
            BackBroker.Trade.Store = BackBroker.Trade.Store.append(trade, ignore_index=True)
            BackBroker.Trade.Store = BackBroker.Trade.Store.set_index(BackBroker.Trade.Store['_id'])

    class Position(object):
        Store = pandas.DataFrame(columns=['symbol', 'quantity', 'margin', 'cost'])

        @staticmethod
        def create(symbol, quantity, margin, cost):
            return pandas.Series(
                index=BackBroker.Position.Store.columns,
                data=[symbol, quantity, margin, cost]
            )

        @staticmethod
        def submit(position):
            BackBroker.Position.Store = BackBroker.Position.Store.append(position, ignore_index=True)
            BackBroker.Position.Store = BackBroker.Position.Store.set_index(BackBroker.Position.Store['symbol'])

    class NetValue(object):
        Store = pandas.DataFrame(columns=['datetime', 'benchmark_value', 'value'])

        @staticmethod
        def create(datetime, benchmark_value, value):
            return pandas.Series(
                index=BackBroker.NetValue.Store.columns,
                data=[datetime, benchmark_value, value]
            )

        @staticmethod
        def submit(info):
            BackBroker.NetValue.Store = BackBroker.NetValue.Store.append(info, ignore_index=True)
            BackBroker.NetValue.Store = BackBroker.NetValue.Store.set_index(BackBroker.NetValue.Store['datetime'])

    class ExchangeInfo(object):
        Store = pandas.DataFrame(columns=['symbol', 'commission_rate', 'leverage', 'price_tick', 'quantity_multiple', 'min_quantity', 'min_notional'])

        @staticmethod
        def create(symbol, commission_rate, leverage, price_tick, quantity_multiple, min_quantity, min_notional):
            return pandas.Series(
                index=BackBroker.ExchangeInfo.Store.columns,
                data=[symbol, commission_rate, leverage, price_tick, quantity_multiple, min_quantity, min_notional]
            )

        @staticmethod
        def submit(info):
            BackBroker.ExchangeInfo.Store = BackBroker.ExchangeInfo.Store.append(info, ignore_index=True)
            BackBroker.ExchangeInfo.Store = BackBroker.ExchangeInfo.Store.set_index(BackBroker.ExchangeInfo.Store['symbol'])

    def __init__(self, callback):
        self.cash = 1000000
        self.datetime = pandas.Timestamp.now()
        self.callback = callback

    @property
    def frozen(self):
        return abs(self.Position.Store['margin'].sum())

    @property
    def available(self):
        return self.cash - self.frozen

    def on_order(self, order):
        self.callback('notify_order', order)

    def on_trade(self, trade):
        self.callback('notify_trade', trade)

    def on_position(self, position):
        self.callback('notify_position', position)

    def on_profit(self, profit):
        self.callback('notify_profit', profit)

    def on_value(self, value):
        self.callback('notify_value', value)

    def update_or_insert_position(self, order):
        cost = order.price * order.quantity
        if order.symbol not in self.Position.Store.index:
            position = self.Position.create(order.symbol, 0, 0, 0)
            self.Position.submit(position)
        position = self.Position.Store.loc[order.symbol]
        if order.side == self.Order.Side.Buy:
            position.cost = position.cost + cost
            quantity = position.quantity + order.quantity
        else:
            position.cost = position.cost - cost
            quantity = position.quantity - order.quantity
        # 当前价格 * 当前数量的绝对值 * 保证金比例 - 上一次保证金 / 上一次数量
        position.margin = order.price * abs(quantity) * order.margin / order.price
        self.Position.Store.loc[order.symbol, ['cost', 'quantity', 'margin']] = [position.cost, position.quantity, position.margin]
        return position

    def settle_order(self, order):
        order.status = self.Order.Status.Completed
        order.traded_quantity = order.quantity
        self.cash = self.cash - order.commission
        position = self.update_or_insert_position(order)
        self.on_position(position)
        return order

    def match_order(self, order):
        order = self.settle_order(order)
        trade = self.Trade.create(order.datetime, order._id, order.symbol, order.side, order.price, order.traded_quantity)
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

    def create_order(self, symbol, side, price, quantity):
        cost = price * quantity
        info = self.ExchangeInfo.Store.loc[symbol]
        margin = cost / info.leverage
        commission = cost * info.commission_rate
        order = self.Order.create(self.datetime, symbol, side, price, quantity, commission, margin, self.Order.Status.Created)
        self.submit_order(order)

    def cancel_order(self, symbol, order_id):
        raise NotImplemented


__all__ = [BackBroker, ]
