from datetime import datetime
from vquant.brokers import Profit
from vquant.stores.ctpstore import CtpStore
from vquant.library.ctp.win64 import thostmduserapi, thosttraderapi
from vquant.utils.catcher import exception_catcher
from vquant.utils.logger import getFileLogger
from vquant.utils.server_check import check_address_port


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
    NotTouched = thosttraderapi.THOST_FTDC_OST_NotTouched
    Touched = thosttraderapi.THOST_FTDC_OST_Touched
    Status = {
        Created: 'Created', Submitted: 'Submitted', Accepted: 'Accepted', Completed: 'Completed', Partial: 'Partial', Canceled: 'Canceled',
        Expired: 'Expired', NotTouched: 'NotTouched', Touched: 'Touched'
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


class MarketApi(thostmduserapi.CThostFtdcMdSpi):
    def __init__(self, on_tick):
        thostmduserapi.CThostFtdcMdSpi.__init__(self)
        self.api = thostmduserapi.CThostFtdcMdApi_CreateFtdcMdApi()
        self.logger = getFileLogger('CTPMarket')
        self.subscribedContracts = list()
        self.nRequestId = 0
        self.on_tick = on_tick

    def OnFrontConnected(self):
        self.logger.info('OnFrontConnected -> OK')
        field = thostmduserapi.CThostFtdcReqUserLoginField()
        self.api.ReqUserLogin(field, self.nRequestId)
        self.nRequestId += 1

    @exception_catcher
    def OnRspUserLogin(self, pRspUserLogin: thostmduserapi.CThostFtdcRspUserLoginField, pRspInfo: thostmduserapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        self.logger.info('OnRspUserLogin -> OK')
        self.api.SubscribeMarketData([contract.encode() for contract in self.subscribedContracts], len(self.subscribedContracts))

    @exception_catcher
    def OnRspSubMarketData(self, pSpecificInstrument: thostmduserapi.CThostFtdcSpecificInstrumentField, pRspInfo: thostmduserapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pSpecificInstrument.InstrumentID not in self.subscribedContracts:
            self.subscribedContracts.append(pSpecificInstrument.InstrumentID)

    @exception_catcher
    def OnRtnDepthMarketData(self, pDepthMarketData: thostmduserapi.CThostFtdcDepthMarketDataField):
        updates = dict(symbol=pDepthMarketData.InstrumentID, price=pDepthMarketData.LastPrice)
        self.on_tick(updates)

    @exception_catcher
    def OnRspError(self, pRspInfo: thostmduserapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        raise TypeError(pRspInfo.ErrorMsg)

    def Start(self, pszFrontAddress):
        if not check_address_port(pszFrontAddress):
            raise ConnectionError('marketFrontAddressNotOpen')
        self.api.RegisterSpi(self)
        self.api.RegisterFront(pszFrontAddress)
        self.api.Init()
        self.api.Join()

    def Stop(self):
        self.api.Release()


class AuthenticateField(object):
    def __init__(self, app_id, auth_code, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcReqAuthenticateField()
        self.field.AppID = app_id
        self.field.AuthCode = auth_code
        self.field.BrokerID = broker_id
        self.field.UserID = investor_id


class UserLoginField(object):
    def __init__(self, broker_id, investor_id, password):
        self.field = thosttraderapi.CThostFtdcReqUserLoginField()
        self.field.BrokerID = broker_id
        self.field.UserID = investor_id
        self.field.Password = password


class QrySettlementInfoField(object):
    def __init__(self, broker_id, investor_id, trading_day):
        self.field = thosttraderapi.CThostFtdcQrySettlementInfoField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.TradingDay = trading_day


class SettlementInfoConfirmField(object):
    def __init__(self, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcSettlementInfoConfirmField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id


class QryTradingAccountField(object):
    def __init__(self, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcQryTradingAccountField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.CurrencyID = 'CNY'


class QryInvestorPositionField(object):
    def __init__(self, broker_id, investor_id, instrument_id):
        self.field = thosttraderapi.CThostFtdcQryInvestorPositionField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.InstrumentID = instrument_id


class OrderInsertField(object):
    def __init__(self, order_ref, broker_id, investor_id, exchange_id, instrument_id, offset_flag, direction, price, volume):
        self.field = thosttraderapi.CThostFtdcInputOrderField()
        self.field.OrderRef = order_ref
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.ExchangeID = exchange_id
        self.field.InstrumentID = instrument_id
        self.field.Direction = direction
        self.field.LimitPrice = price
        self.field.VolumeTotalOriginal = volume
        self.field.OrderPriceType = thosttraderapi.THOST_FTDC_OPT_LimitPrice
        self.field.ContingentCondition = thosttraderapi.THOST_FTDC_CC_Immediately
        self.field.TimeCondition = thosttraderapi.THOST_FTDC_TC_IOC
        self.field.VolumeCondition = thosttraderapi.THOST_FTDC_VC_AV
        self.field.CombHedgeFlag = thosttraderapi.THOST_FTDC_HF_Speculation
        self.field.CombOffsetFlag = offset_flag
        self.field.ForceCloseReason = thosttraderapi.THOST_FTDC_FCC_NotForceClose


class TraderApi(thosttraderapi.CThostFtdcTraderSpi):
    def __init__(self, broker, app_id, auth_code, broker_id, investor_id, password):
        thosttraderapi.CThostFtdcTraderSpi.__init__(self)
        self.broker = broker
        self.api = thosttraderapi.CThostFtdcTraderApi_CreateFtdcTraderApi()
        self.app_id = app_id
        self.auth_code = auth_code
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.password = password
        self._request_id = 0
        self.logger = getFileLogger('CTPTrader')
        self.front_id = 0
        self.session_id = 0
        self.trading_day = None
        self._order_ref = 0
        self.logged = False

    @property
    def order_ref(self):
        self._order_ref += 1
        return self._order_ref

    @property
    def request_id(self):
        self._request_id += 1
        return self._request_id

    def auth(self):
        self.api.ReqAuthenticate(AuthenticateField(self.app_id, self.auth_code, self.broker_id, self.investor_id).field, self.request_id)

    def login(self):
        self.api.ReqUserLogin(UserLoginField(self.broker_id, self.investor_id, self.password).field, self.request_id)

    def sync_asset(self):
        self.api.ReqQryTradingAccount(QryTradingAccountField(self.broker_id, self.investor_id).field, self.request_id)

    def sync_position(self, instrument_id):
        self.api.ReqQryInvestorPosition(QryInvestorPositionField(self.broker_id, self.investor_id, instrument_id).field, self.request_id)

    def create_order(self, exchange_id, instrument_id, offset_flag, direction, price, volume):
        self.api.ReqOrderInsert(OrderInsertField(self.order_ref, self.broker_id, self.investor_id, exchange_id, instrument_id, offset_flag, direction, price, volume).field, self.request_id)

    def get_settlement_info(self, trading_day):
        self.api.ReqQrySettlementInfo(QrySettlementInfoField(self.broker_id, self.investor_id, trading_day).field, self.request_id)

    def confirm_settlement_info(self):
        self.api.ReqSettlementInfoConfirm(SettlementInfoConfirmField(self.broker_id, self.investor_id).field, self.request_id)

    @exception_catcher
    def OnFrontConnected(self):
        self.logger.info('OnFrontConnected -> OK')
        self.auth()

    @exception_catcher
    def OnRspAuthenticate(self, pRspAuthenticateField: thosttraderapi.CThostFtdcRspAuthenticateField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        self.logger.info('OnRspAuthenticate -> OK')
        if bIsLast:
            self.login()

    @exception_catcher
    def OnRspUserLogin(self, pRspUserLogin: thosttraderapi.CThostFtdcRspUserLoginField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        self.logger.info('OnRspUserLogin')
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        self.broker.on_login(dict(front_id=pRspUserLogin.FrontID, session_id=pRspUserLogin.SessionID, trading_day=pRspUserLogin.TradingDay, max_order_ref=pRspUserLogin.MaxOrderRef, login=True))

    @exception_catcher
    def OnRspQryInvestorPosition(self, pInvestorPosition: thosttraderapi.CThostFtdcInvestorPositionField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        if not pInvestorPosition:
            return
        self.broker.on_position(symbol=pInvestorPosition.InstrumentID, exchange_id=pInvestorPosition.ExchangeID, position_date=pInvestorPosition.PositionDate, direction=pInvestorPosition.PosiDirection, cost=pInvestorPosition.PositionCost, margin=pInvestorPosition.FrozenMargin, volume=pInvestorPosition.Position, today_volume=pInvestorPosition.TodayPosition, yesterday_volume=pInvestorPosition.YdPosition)

    @exception_catcher
    def OnRspQrySettlementInfo(self, pSettlementInfo: thosttraderapi.CThostFtdcSettlementInfoField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        self.logger.info('OnRspQrySettlementInfo -> OK')

    @exception_catcher
    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: thosttraderapi.CThostFtdcSettlementInfoConfirmField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        self.logger.info('OnRspSettlementInfoConfirm -> OK')

    @exception_catcher
    def OnRspQryTradingAccount(self, pTradingAccount: thosttraderapi.CThostFtdcTradingAccountField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        if not pTradingAccount:
            return
        self.broker.on_asset(cash=pTradingAccount.Balance, available=pTradingAccount.Available, frozen=pTradingAccount.FrozenMargin, position_profit=pTradingAccount.PositionProfit, close_profit=pTradingAccount.CloseProfit)

    @exception_catcher
    def OnRspOrderInsert(self, pInputOrder: thosttraderapi.CThostFtdcInputOrderField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo.ErrorID == 9:
            self.confirm_settlement_info()
        raise TypeError(pRspInfo.ErrorMsg)

    @exception_catcher
    def OnRtnOrder(self, pOrder: thosttraderapi.CThostFtdcOrderField):
        if not pOrder or not pOrder.OrderSysID:
            return
        self.broker.on_order(exchange_id=pOrder.ExchangeID, order_sys_id=pOrder.OrderSysID, insert_date=pOrder.InsertDate, update_time=pOrder.UpdateTime, symbol=pOrder.InstrumentID, flag=pOrder.CombOffsetFlag, side=pOrder.Direction, price=pOrder.LimitPrice, volume=pOrder.VolumeTotalOriginal, status=pOrder.OrderStatus)

    @exception_catcher
    def OnRtnTrade(self, pTrade: thosttraderapi.CThostFtdcTradeField):
        if not pTrade:
            return
        self.broker.on_trade(trade_id=pTrade.TradeID, trade_date=pTrade.TradeDate, trade_time=pTrade.TradeTime, exchange_id=pTrade.ExchangeID, order_sys_id=pTrade.OrderSysID, symbol=pTrade.InstrumentID, flag=pTrade.OffsetFlag, side=pTrade.Direction, price=pTrade.Price, volume=pTrade.Volume)

    @exception_catcher
    def OnRspError(self, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        raise TypeError(pRspInfo.ErrorMsg)

    def Start(self, pszFrontAddress):
        if not check_address_port(pszFrontAddress):
            raise ConnectionError('tradeFrontAddressNotOpen')
        self.api.RegisterSpi(self)
        self.api.RegisterFront(pszFrontAddress)
        self.api.SubscribePrivateTopic(thosttraderapi.THOST_TERT_QUICK)
        self.api.SubscribePublicTopic(thosttraderapi.THOST_TERT_QUICK)
        self.api.Init()
        self.api.Join()

    def Stop(self):
        self.api.Release()


class CtpFutureBroker(object):
    def __init__(self, cerebro, **kwargs):
        self.cerebro = cerebro
        self.ticker = TraderApi(broker=self, app_id=kwargs.get('app_id'), auth_code=kwargs.get('auth_code'), broker_id=kwargs.get('broker_id'), investor_id=kwargs.get('investor_id'), password=kwargs.get('password'))
        self.cash = 0
        self.value = 0
        self.available = 0
        self.frozen = 0
        self.profit = 0
        self.symbols = dict()
        self.store = CtpStore()

    @property
    def is_logged(self):
        return self.ticker.logged

    def add_symbol(self, symbol, info):
        self.symbols[symbol] = info

    @staticmethod
    def get_profit(direction, volume_multiple, cost_price, price, volume):
        profit = (price - cost_price) * volume_multiple * volume
        if direction == Position.Short:
            profit = (cost_price - price) * volume_multiple * volume
        return profit

    def get_orders(self, symbol, side):
        status = [thosttraderapi.THOST_FTDC_OST_PartTradedQueueing, thosttraderapi.THOST_FTDC_OST_NoTradeQueueing, thosttraderapi.THOST_FTDC_OST_NoTradeNotQueueing, thosttraderapi.THOST_FTDC_OST_NotTouched, thosttraderapi.THOST_FTDC_OST_Touched]
        return self.store.query_orders(symbol, side, status)

    def get_position(self, symbol, direction):
        pandas_data = self.store.query_position(symbol, direction)
        if not len(pandas_data.index):
            return Position(symbol, 0, direction, 0, 0, 0, 0, 0, 0, 0, 0)
        record = pandas_data.iloc[0]
        return Position(record.symbol, record.cost, record.direction, record.volume, record.margin, record.today_cost, record.yesterday_cost, record.today_margin, record.yesterday_margin, record.today_volume, record.yesterday_volume)

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
            if flag == Order.CloseToday:
                position.today_cost -= cost
                position.today_margin -= margin
                position.today_volume -= volume
            if flag == Order.CloseYesterday:
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
        order = Order(exchange_id, order_sys_id, insert_date, update_time, symbol, flag, side, price, volume, status, 0, 0)
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
        trade = Trade(trade_id, trade_date, trade_time, exchange_id, order_sys_id, symbol, flag, side, price, volume, 0)
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
        if date == Position.Today:
            position.today_cost = cost
            position.today_volume = today_volume
            position.today_margin = margin
            position.yesterday_volume = yesterday_volume if yesterday_volume else position.yesterday_volume
        if date == Position.History:
            position.yesterday_cost = cost
            position.yesterday_margin = margin
            position.yesterday_volume = volume
        position.cost = position.today_cost + position.yesterday_cost
        position.margin = position.today_margin + position.yesterday_margin
        position.volume = position.today_volume + position.yesterday_volume
        self.on_position(position.symbol, position.cost, position.direction, position.volume, position.margin, position.today_cost, position.yesterday_cost, position.today_margin, position.yesterday_margin, position.today_volume, position.yesterday_volume)

    def on_position(self, symbol, cost, direction, volume, margin, today_cost, yesterday_cost, today_margin, yesterday_margin, today_volume, yesterday_volume):
        position = Position(symbol, cost, direction, volume, margin, today_cost, yesterday_cost, today_margin, yesterday_margin, today_volume, yesterday_volume)
        self.store.update_or_insert_position(position.__dict__())
        self.cerebro.notify_position(position)

    def on_profit(self, dt, amount):
        profit = Profit(dt, amount)
        self.store.insert_profit(profit.__dict__())
        self.cerebro.notify_profit(profit)

    @staticmethod
    def in_shanghai(exchange):
        return exchange in ('SHFE', 'INE')

    def close(self, exchange, symbol, side, price, volume):
        if self.in_shanghai(exchange):
            direction = Position.Short if side == Order.Buy else Position.Long
            position = self.get_position(symbol, direction)
            if position.yesterday_volume > volume:
                self.ticker.create_order(exchange, symbol, Order.CloseYesterday, side, price, volume)
            else:
                self.ticker.create_order(exchange, symbol, Order.CloseYesterday, side, price, position.yesterday_volume)
                self.ticker.create_order(exchange, symbol, Order.CloseToday, side, price, volume - position.yesterday_volume)
        else:
            self.ticker.create_order(exchange, symbol, Order.Close, side, price, volume)

    def close_today(self, exchange, symbol, side, price, volume):
        if self.in_shanghai(exchange):
            self.ticker.create_order(exchange, symbol, Order.CloseToday, side, price, volume)
        else:
            self.ticker.create_order(exchange, symbol, Order.Close, side, price, volume)

    def close_yesterday(self, exchange, symbol, side, price, volume):
        if self.in_shanghai(exchange):
            self.ticker.create_order(exchange, symbol, Order.CloseYesterday, side, price, volume)
        else:
            self.ticker.create_order(exchange, symbol, Order.Close, side, price, volume)

    def create_order(self, _, symbol, flag, side, price, volume):
        exchange = self.symbols[symbol]['exchange_id']
        if flag == Order.Close:
            self.close(exchange, symbol, side, price, volume)
        elif flag == Order.CloseToday:
            self.close_today(exchange, symbol, side, price, volume)
        elif flag == Order.CloseYesterday:
            self.close_yesterday(exchange, symbol, side, price, volume)
        else:
            self.ticker.create_order(exchange, symbol, flag, side, price, volume)
