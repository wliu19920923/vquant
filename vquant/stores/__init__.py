# import pandas
#
#
# class OrderStore(pandas.DataFrame):
#     fields = [
#         'id', 'datetime', 'symbol', 'flag', 'side', 'price', 'volume', 'commission', 'margin', 'status'
#     ]
#
#     def __init__(self):
#         super(OrderStore, self).__init__(columns=self.fields)
#
#
# class TradeStore(pandas.DataFrame):
#     fields = ['id', 'datetime', 'symbol', 'order_id', 'flag', 'side', 'price', 'volume', 'profit']
#
#     def __init__(self):
#         super(TradeStore, self).__init__(columns=self.fields)
#
#
# class PositionStore(pandas.DataFrame):
#     fields = ['symbol', 'cost', 'direction', 'volume', 'margin']
#
#     def __init__(self):
#         super(PositionStore, self).__init__(columns=self.fields)
#
#
# class ProfitStore(pandas.DataFrame):
#     fields = ['datetime', 'amount']
#
#     def __init__(self):
#         super(ProfitStore, self).__init__(columns=self.fields)
#
#
# class ValueStore(pandas.DataFrame):
#     fields = ['datetime', 'value', 'benchmark_value']
#
#     def __init__(self):
#         super(ValueStore, self).__init__(columns=self.fields)
#
#
# class Store(object):
#     def __init__(self):
#         self.orders = OrderStore()
#         self.trades = TradeStore()
#         self.positions = PositionStore()
#         self.profits = ProfitStore()
#         self.values = ValueStore()
#
#     def update_or_insert_order(self, order):
#         record = self.orders.loc[self.orders['id'] == order['id']]
#         if len(record.index) > 0:
#             self.orders.loc[record.index, OrderStore.fields] = list(order.values())
#         else:
#             self.orders = self.orders.append([order], ignore_index=True)
#
#     def update_or_insert_position(self, position):
#         record = self.positions.loc[(self.positions['symbol'] == position['symbol']) & (self.positions['direction'] == position['direction'])]
#         if len(record.index) > 0:
#             self.positions.loc[record.index, PositionStore.fields] = list(position.values())
#         else:
#             self.positions = self.positions.append([position], ignore_index=True)
#
#     def insert_trade(self, trade):
#         self.trades = self.trades.append([trade], ignore_index=True)
#
#     def insert_value(self, value):
#         self.values = self.values.append([value], ignore_index=True)
#
#     def insert_profit(self, profit):
#         self.profits = self.profits.append([profit], ignore_index=True)
#
#     def query_position(self, symbol, direction):
#         return self.positions.loc[(self.positions['symbol'] == symbol) & (self.positions['direction'] == direction)]
#
#     def query_orders(self, symbol, side, status):
#         return self.orders.loc[(self.orders['symbol'] == symbol) & (self.orders['side'] == side) & self.orders['status'].isin(status)]


from pandas import DataFrame


class LocalStore(object):
    def __init__(self, columns: [str]):
        self.frame = DataFrame(columns=columns)

    def query(self, **kwargs):
        _frame = self.frame
        for key, value in kwargs.items():
            _frame = _frame.loc[_frame[key] == value]
        return _frame

    def update_or_insert(self, row: dict, **kwargs):
        _frame = self.query(**kwargs)
        updated_rows = len(_frame.index)
        if updated_rows:
            self.frame.loc[_frame.index, self.frame.columns] = list(row.values())
        else:
            self.frame = self.frame.append([row], ignore_index=True)
        return updated_rows

    def delete(self, **kwargs):
        _frame = self.query(**kwargs)
        drop_rows = len(_frame.index)
        if drop_rows:
            self.frame.drop(index=_frame.index, inplace=True)
        return drop_rows
