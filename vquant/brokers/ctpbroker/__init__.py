from trader import TraderApi
from vquant.stores.ctpstore import Store
from vquant.brokers import Position
from vquant.library.ctp.win64 import thosttraderapi


class CtpBroker(object):
    def __init__(self, **kwargs):
        self.ticker = TraderApi(broker=self, app_id=kwargs.get('app_id'), auth_code=kwargs.get('auth_code'), broker_id=kwargs.get('broker_id'), investor_id=kwargs.get('investor_id'), password=kwargs.get('password'))
        self.cash = 0
        self.value = 0
        self.available = 0
        self.frozen = 0
        self.profit = 0
        self.symbols = dict()
        self.store = Store()

    @property
    def is_logged(self):
        return self.ticker.logged

    def add_symbol(self, symbol, info):
        self.symbols[symbol] = info

    def get_orders(self, symbol):
        return self.store.query_orders(symbol)

    def get_position(self, symbol, direction):
        pandas_data = self.store.query_position(symbol, direction)
        if not len(pandas_data.index):
            return Position(symbol, 0, direction, 0, 0)
        record = pandas_data.iloc[0]
        return Position(record.symbol, record.cost, record.direction, record.volume, record.margin)

    def get_profit(self, direction, volume_multiple, cost_price, price, volume):
        profit = (price - cost_price) * volume_multiple * volume
        if direction == thosttraderapi.THOST_FTDC_PD_Short:
            profit = (cost_price - price) * volume_multiple * volume
        return profit

    def update_position(self, position, flag, cost_price, price, volume, volume_multiple):
        margin_rate = self.symbols[position.symbol]['margin_rate']
        if flag == thosttraderapi.THOST_FTDC_OF_Open:
            cost = price * volume * volume_multiple
            position_cost = position.cost + cost
            position_margin = position.margin + cost * margin_rate
            position_volume = position.volume + volume
        else:
            cost = cost_price * volume * volume_multiple
            position_cost = position.cost - cost
            position_margin = position.margin - cost * margin_rate
            position_volume = position.volume - volume
        self.on_position(position.symbol, position_cost, position.direction, position_volume, position_margin)

    def on_value(self, value):
        self.store.insert_value(value)

    def on_asset(self, cash, available, frozen, position_profit, close_profit):
        self.cash = cash
        self.available = available
        self.frozen = frozen
        self.value = available + frozen + position_profit
        self.profit = position_profit + close_profit
        self.on_value(self.value)

    def on_order(self, oid, datetime, symbol, order_ref, order_sys_id, exchange_id, side, price, volume, status):
        record = dict(id=oid, datetime=datetime, symbol=symbol, order_ref=order_ref, order_sys_id=order_sys_id, exchange_id=exchange_id, side=side, price=price, volume=volume, status=status)
        self.store.update_or_insert_order(record)

    def on_trade(self, tid, datetime, trade_id, order_id, symbol, exchange_id, flag, side, price, volume):
        direction = thosttraderapi.THOST_FTDC_PD_Long if side == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Short
        if flag != thosttraderapi.THOST_FTDC_OF_Open:
            direction = thosttraderapi.THOST_FTDC_PD_Short if side == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Long
        position = self.get_position(symbol, direction)
        volume_multiple = self.symbols[position.symbol]['volume_multiple']
        cost_price = position.cost / volume_multiple / position.volume
        profit = self.get_profit(direction, volume_multiple, cost_price, price, volume)
        record = dict(id=tid, datetime=datetime, trade_id=trade_id, order_id=order_id, symbol=symbol, exchange_id=exchange_id, flag=flag, side=side, price=price, volume=volume, profit=profit)
        self.store.insert_trade(record)
        self.update_position(position, flag, cost_price, price, volume, volume_multiple)
        self.on_profit(datetime, profit)

    def on_position(self, symbol, cost, direction, volume, margin):
        record = dict(symbol=symbol, cost=cost, direction=direction, volume=volume, margin=margin)
        self.store.update_or_insert_position(record)

    def on_profit(self, datetime, amount):
        record = dict(datetime=datetime, amount=amount)
        self.store.insert_profit(record)
