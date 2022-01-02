import pandas
from vquant.order import Order
from position import Position


class OrderStore(pandas.DataFrame):
    fields = [
        'order_id', 'create_time', 'update_time', 'symbol', 'flag', 'side', 'type', 'price', 'deal_price',
        'volume_origin', 'volume_traded', 'volume_total', 'order_status'
    ]

    def __init__(self):
        super(OrderStore, self).__init__(columns=self.fields)


class TradeStore(pandas.DataFrame):
    fields = ['trade_id', 'create_time', 'symbol', 'order_id', 'offset_flag', 'direction', 'price', 'volume', 'margin', 'profit']

    def __init__(self):
        super(TradeStore, self).__init__(columns=self.fields)


class PositionStore(pandas.DataFrame):
    fields = ['symbol', 'cost', 'direction', 'volume', 'margin', 'profit']

    def __init__(self):
        super(PositionStore, self).__init__(columns=self.fields)


class ProfitStore(pandas.DataFrame):
    fields = ['timestamp', 'profit']

    def __init__(self):
        super(ProfitStore, self).__init__(columns=self.fields)


class Store(object):
    def __init__(self):
        self.orders = OrderStore()
        self.trades = TradeStore()
        self.positions = PositionStore()
        self.profits = ProfitStore()

    def update_or_insert_order(self, order):
        record = self.orders.loc[self.orders['order_id'] == order['order_id']]
        if len(record.index) > 0:
            self.orders.loc[record.index, self.orders.fields] = list(record.values())
        else:
            self.orders = self.orders.append([order], ignore_index=True)

    def update_or_insert_position(self, position):
        record = self.positions.loc[(self.positions['symbol'] == position['symbol']) & (self.positions['direction'] == position['direction'])]
        if len(record.index) > 0:
            self.positions.loc[record.index, self.orders.fields] = list(record.values())
        else:
            self.positions = self.positions.append([position], ignore_index=True)

    def insert_profit(self, profit):
        self.profits = self.profits.append([profit], ignore_index=True)

    def insert_trade(self, trade):
        self.trades = self.trades.append([trade], ignore_index=True)

    def active_orders(self):
        return self.orders.loc[self.orders['status'].isin([Order.Created, Order.Submitted, Order.Accepted, Order.Partial])]

    def query_position(self, symbol, direction):
        return self.positions.loc[(self.positions['symbol'] == symbol) & (self.positions['direction'] == direction)]

