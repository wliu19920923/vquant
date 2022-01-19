from datetime import datetime
from trader import TraderApi
from vquant.brokers import Profit
from vquant.stores.ctpstore import Store
from vquant.library.ctp.win64 import thosttraderapi


class CtpBroker(object):
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
        Open, Close, CloseToday, CloseYesterday = thosttraderapi.THOST_FTDC_OF_Open, thosttraderapi.THOST_FTDC_OF_Close, thosttraderapi.THOST_FTDC_OF_CloseToday, thosttraderapi.THOST_FTDC_OF_CloseYesterday
        Flags = {Open: 'Open', Close: 'Close', CloseToday: 'CloseToday', CloseYesterday: 'CloseYesterday'}

        Buy, Sell = thosttraderapi.THOST_FTDC_D_Buy, thosttraderapi.THOST_FTDC_D_Sell
        Sides = {Buy: 'Buy', Sell: 'Sell'}

        Created = thosttraderapi.THOST_FTDC_OST_Unknown
        Submitted = thosttraderapi.THOST_FTDC_OST_NoTradeNotQueueing
        Accepted = thosttraderapi.THOST_FTDC_OST_NoTradeQueueing
        Completed = thosttraderapi.THOST_FTDC_OST_AllTraded
        Partial = thosttraderapi.THOST_FTDC_OST_PartTradedQueueing
        Canceled = thosttraderapi.THOST_FTDC_OST_Canceled
        Expired = thosttraderapi.THOST_FTDC_OST_PartTradedNotQueueing
        Margin = thosttraderapi.THOST_FTDC_OST_Canceled
        Rejected = thosttraderapi.THOST_FTDC_OST_Canceled
        NotTouched = thosttraderapi.THOST_FTDC_OST_NotTouched
        Touched = thosttraderapi.THOST_FTDC_OST_Touched
        Status = {
            Created: 'Created', Submitted: 'Submitted', Accepted: 'Accepted', Completed: 'Completed', Partial: 'Partial', Canceled: 'Canceled',
            Expired: 'Expired', Margin: 'Margin', Rejected: 'Rejected', NotTouched: 'NotTouched', Touched: 'Touched'
        }

        def __init__(self, exchange_id, order_sys_id, insert_date, update_time, symbol, flag, side, price, volume, status, commission, margin):
            self.id = exchange_id + order_sys_id
            self.datetime = datetime.strptime(insert_date + update_time, '%Y%m%d%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
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
        def __init__(self, trade_id, trade_date, trade_time, exchange_id, order_sys_id, symbol, flag, side, price, volume, profit):
            self.id = exchange_id + trade_id
            self.datetime = datetime.strptime(trade_date + trade_time, '%Y%m%d%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            self.order_id = exchange_id + order_sys_id
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
        Today, History = thosttraderapi.THOST_FTDC_PSD_Today, thosttraderapi.THOST_FTDC_PSD_History
        Dates = {Today: 'Today', History: 'History'}

        Long, Short = thosttraderapi.THOST_FTDC_PD_Long, thosttraderapi.THOST_FTDC_PD_Short
        Directions = {Long: 'Long', Short: 'Short'}

        def __init__(self, symbol, cost, direction, volume, margin, today_cost, yesterday_cost, today_margin, yesterday_margin, today_volume, yesterday_volume):
            self.symbol = symbol
            self.cost = cost
            self.direction = direction
            self.volume = volume
            self.margin = margin
            self.today_cost = today_cost
            self.yesterday_cost = yesterday_cost
            self.today_margin = today_margin
            self.yesterday_margin = yesterday_margin
            self.today_volume = today_volume
            self.yesterday_volume = yesterday_volume

        def __dict__(self):
            return {
                'symbol': self.symbol,
                'cost': self.cost,
                'direction': self.direction,
                'volume': self.volume,
                'margin': self.margin,
                'today_cost': self.today_cost,
                'yesterday_cost': self.yesterday_cost,
                'today_margin': self.today_margin,
                'yesterday_margin': self.yesterday_margin,
                'today_volume': self.today_volume,
                'yesterday_volume': self.yesterday_volume
            }

    def __init__(self, cerebro, **kwargs):
        self.cerebro = cerebro
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

    def get_orders(self, symbol, side):
        status = [thosttraderapi.THOST_FTDC_OST_PartTradedQueueing, thosttraderapi.THOST_FTDC_OST_NoTradeQueueing, thosttraderapi.THOST_FTDC_OST_NoTradeNotQueueing, thosttraderapi.THOST_FTDC_OST_NotTouched, thosttraderapi.THOST_FTDC_OST_Touched]
        return self.store.query_orders(symbol, side, status)

    def get_position(self, symbol, direction):
        pandas_data = self.store.query_position(symbol, direction)
        if not len(pandas_data.index):
            return self.Position(symbol, 0, direction, 0, 0, 0, 0, 0, 0, 0, 0)
        record = pandas_data.iloc[0]
        return self.Position(record.symbol, record.cost, record.direction, record.volume, record.margin, record.today_cost, record.yesterday_cost, record.today_margin, record.yesterday_margin, record.today_volume, record.yesterday_volume)

    def get_profit(self, direction, volume_multiple, cost_price, price, volume):
        profit = (price - cost_price) * volume_multiple * volume
        if direction == self.Position.Short:
            profit = (cost_price - price) * volume_multiple * volume
        return profit

    def update_position(self, position, flag, cost_price, price, volume, volume_multiple):
        margin_rate = self.symbols[position.symbol]['margin_rate']
        if flag == thosttraderapi.THOST_FTDC_OF_Open:
            cost = price * volume * volume_multiple
            position.cost += cost
            position.margin += cost * margin_rate
            position.volume += volume
        else:
            cost = cost_price * volume * volume_multiple
            margin = cost * margin_rate
            position.cost -= cost
            position.margin -= margin
            position.volume -= volume
            if flag == self.Order.CloseToday:
                position.today_cost -= cost
                position.today_margin -= margin
                position.today_volume -= volume
            if flag == self.Order.CloseYesterday:
                position.yesterday_cost -= cost
                position.yesterday_margin -= margin
                position.yesterday_volume -= volume
        self.on_position(position.symbol, position.cost, position.direction, position.volume, position.margin, position.today_cost, position.yesterday_cost, position.today_margin, position.yesterday_margin, position.today_volume, position.yesterday_volume)

    def on_value(self, value):
        self.store.insert_value(value)

    def on_asset(self, cash, available, frozen, position_profit, close_profit):
        self.cash = cash
        self.available = available
        self.frozen = frozen
        self.value = available + frozen + position_profit
        self.profit = position_profit + close_profit
        self.on_value(self.value)

    def on_order(self, exchange_id, order_sys_id, insert_date, update_time, symbol, flag, side, price, volume, status):
        order = self.Order(exchange_id, order_sys_id, insert_date, update_time, symbol, flag, side, price, volume, status, 0, 0)
        volume_multiple = self.symbols[order.symbol]['volume_multiple']
        commission_rate = self.symbols[order.symbol]['commission_rate']
        cost = order.price * order.volume * volume_multiple
        order.commission = cost * commission_rate
        if order.flag == order.Open:
            margin_rate = self.symbols[order.symbol]['margin_rate']
            order.margin = cost * margin_rate
        self.store.update_or_insert_order(order.__dict__())
        self.cerebro.notify_order(order)

    def on_trade(self, trade_id, trade_date, trade_time, exchange_id, order_sys_id, symbol, flag, side, price, volume):
        trade = self.Trade(trade_id, trade_date, trade_time, exchange_id, order_sys_id, symbol, flag, side, price, volume, 0)
        direction = thosttraderapi.THOST_FTDC_PD_Long if trade.side == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Short
        if trade.flag != thosttraderapi.THOST_FTDC_OF_Open:
            direction = thosttraderapi.THOST_FTDC_PD_Short if trade.side == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Long
        position = self.get_position(trade.symbol, direction)
        volume_multiple = self.symbols[position.symbol]['volume_multiple']
        cost_price = position.cost / volume_multiple / position.volume
        trade.profit = self.get_profit(direction, volume_multiple, cost_price, price, volume)
        self.store.insert_trade(trade.__dict__())
        self.cerebro.notify_trade(trade)
        self.update_position(position, flag, cost_price, price, volume, volume_multiple)
        self.on_profit(trade.datetime, trade.profit)

    def on_date_position(self, symbol, date, cost, direction, volume, margin, today_volume, yesterday_volume):
        position = self.get_position(symbol, direction)
        if date == self.Position.Today:
            position.today_cost = cost
            position.today_volume = today_volume
            position.today_margin = margin
            position.yesterday_volume = yesterday_volume if yesterday_volume else position.yesterday_volume
        if date == self.Position.History:
            position.yesterday_cost = cost
            position.yesterday_margin = margin
            position.yesterday_volume = volume
        position.cost = position.today_cost + position.yesterday_cost
        position.margin = position.today_margin + position.yesterday_margin
        position.volume = position.today_volume + position.yesterday_volume
        self.on_position(position.symbol, position.cost, position.direction, position.volume, position.margin, position.today_cost, position.yesterday_cost, position.today_margin, position.yesterday_margin, position.today_volume, position.yesterday_volume)

    def on_position(self, symbol, cost, direction, volume, margin, today_cost, yesterday_cost, today_margin, yesterday_margin, today_volume, yesterday_volume):
        position = self.Position(symbol, cost, direction, volume, margin, today_cost, yesterday_cost, today_margin, yesterday_margin, today_volume, yesterday_volume)
        self.store.update_or_insert_position(position.__dict__())
        self.cerebro.notify_position(position)

    def on_profit(self, dt, amount):
        profit = Profit(dt, amount)
        self.store.insert_profit(profit.__dict__())
        self.cerebro.notify_profit(profit)

    def create_order(self, _, symbol, flag, side, price, volume):
        exchange_id = self.symbols[symbol]['exchange_id']
        self.ticker.create_order(exchange_id, symbol, flag, side, price, volume)
