import os
import pandas
from vquant.library.ctp.win64 import thosttraderapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PositionRecord(object):
    fields = ['symbol', 'exchange_id', 'hedge_flag', 'position_date', 'direction', 'volume', 'today_volume', 'yesterday_volume', 'cost', 'margin']

    def __init__(self):
        self.records = pandas.DataFrame(columns=self.fields)

    def update_or_insert(self, symbol, exchange_id, position_date, direction, volume, today_volume, yesterday_volume, cost, margin):
        record = dict(symbol=symbol, exchange_id=exchange_id, position_date=position_date, direction=direction, volume=volume, today_position=today_position, yesterday_position=yesterday_position, position_cost=position_cost)
        records = self.records.loc[(self.records['symbol'] == symbol) & (self.records['position_date'] == position_date) & (self.records['direction'] == direction)]
        if len(records.index) > 0:
            self.records.loc[records.index, self.fields] = list(record.values())
        else:
            self.records = self.records.append([record], ignore_index=True)
        return record

    def update_by_trade(self, symbol, exchange_id, offset_flag, direction, price, volume, volume_multiple):
        if offset_flag == thosttraderapi.THOST_FTDC_OF_Open:
            position_cost = price * volume * volume_multiple
            direction = thosttraderapi.THOST_FTDC_PD_Long if direction == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Short
            records = self.records.loc[(self.records['symbol'] == symbol) & (self.records['position_date'] == thosttraderapi.THOST_FTDC_PSD_Today) & (self.records['direction'] == direction)]
            if records:
                record = records[0]
                position_cost += record['position_cost']
                volume = record['volume'] + volume
                today_position = record['today_position'] + volume
                self.records.loc[records.index, ['position_cost', 'volume', 'today_position']] = [position_cost, volume, today_position]
            else:
                self.update_or_insert(symbol, exchange_id, thosttraderapi.THOST_FTDC_PSD_Today, direction, volume, volume, 0, position_cost)
        else:
            position_date = thosttraderapi.THOST_FTDC_PSD_History if offset_flag == thosttraderapi.THOST_FTDC_OF_CloseYesterday else thosttraderapi.THOST_FTDC_PSD_Today
            direction = thosttraderapi.THOST_FTDC_PD_Short if direction == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Long
            records = self.records.loc[(self.records['symbol'] == symbol) & (self.records['position_date'] == position_date) & (self.records['direction'] == direction)]
            if records:
                record = records[0]
                position_cost = record['position_cost'] - record['position_cost'] / record['volume'] * volume
                volume = record['volume'] - volume
                today_position = record['today_position'] - volume
                self.update_or_insert(symbol, exchange_id, position_date, direction, volume, today_position, record['yesterday_position'], position_cost)

    def get_volume(self, symbol, direction):
        records = self.records.loc[(self.records['symbol'] == symbol) & (self.records['direction'] == direction)]
        return records['volume'].sum()

    def get_today_position(self, symbol, direction):
        records = self.records.loc[(self.records['symbol'] == symbol) & self.records['position_date'] == thosttraderapi.THOST_FTDC_PSD_Today & (self.records['direction'] == direction)]
        return records['today_position'].sum()

    def get_yesterday_position(self, symbol, direction):
        return self.get_volume(symbol, direction) - self.get_today_position(symbol, direction)

    def get_volume_cost(self, symbol, direction):
        records = self.records.loc[(self.records['symbol'] == symbol) & self.records['position_date'] == thosttraderapi.THOST_FTDC_PSD_Today & (self.records['direction'] == direction)]
        return records['position_cost'].sum()

    def get_avg_position_cost(self, symbol, direction, volume_multiple):
        volume = self.get_volume(symbol, direction)
        volume_cost = self.get_volume_cost(symbol, direction)
        return volume_cost / volume_multiple / volume

    def query(self, symbol):
        return self.records.loc[self.records['symbol'] == symbol].to_dict(orient='records')


class AccountRecord(object):
    def __init__(self, available=0, frozen=0, position_profit=0, close_profit=0):
        self.available = available
        self.frozen = frozen
        self.position_profit = position_profit
        self.close_profit = close_profit

    @property
    def net_value(self):
        return self.available + self.frozen + self.position_profit

    @property
    def profit(self):
        return self.position_profit + self.close_profit


class OrderRecord(object):
    fields = ['id', 'order_ref', 'datetime', 'symbol', 'exchange_id', 'flag', 'side', 'price', 'volume', 'volume_traded', 'volume_total', 'status']

    def __init__(self):
        self.records = pandas.DataFrame(columns=self.fields)

    def update_or_insert(self, order_ref, order_sys_id, symbol, exchange_id, offset_flag, direction, price, volume, volume_traded, volume_total, status):
        record = dict(order_ref=order_ref, order_sys_id=order_sys_id, symbol=symbol, exchange_id=exchange_id, offset_flag=offset_flag, direction=direction, price=price, volume=volume, volume_traded=volume_traded, volume_total=volume_total, status=status)
        records = self.records.loc[(self.records['order_sys_id'] == order_sys_id) & (self.records['exchange_id'] == exchange_id)]
        if len(records.index) > 0:
            self.records.loc[records.index, self.fields] = list(record.values())
        else:
            self.records = self.records.append([record], ignore_index=True)
        return record

    def get_current_delegate(self):
        return self.records.loc[(self.records['status'] != thosttraderapi.THOST_FTDC_OST_Canceled) & (self.records['status'] != thosttraderapi.THOST_FTDC_OST_AllTraded)].to_dict(orient='records')

    def query(self, symbol):
        return self.records.loc[self.records['symbol'] == symbol].to_dict(orient='records')


class TradeRecord(object):
    fields = ['id', 'datetime', 'order_id', 'symbol', 'exchange_id', 'flag', 'side', 'price', 'volume', 'profit']

    def __init__(self):
        self.records = pandas.DataFrame(columns=self.fields)

    def insert(self, id, datetime, order_id, symbol, exchange_id, flag, side, price, volume, profit):
        record = dict(id=id, datetime=datetime, order_id=order_id, symbol=symbol, exchange_id=exchange_id, flag=flag, side=side, price=price, volume=volume, profit=profit)
        self.records = self.records.append([record], ignore_index=True)

    def query(self, symbol):
        return self.records.loc[self.records['symbol'] == symbol].to_dict(orient='records')

