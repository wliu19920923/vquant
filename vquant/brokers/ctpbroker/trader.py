from vquant.utils import exception_catcher
from vquant.utils.logger import get_logger
from vquant.utils.server_check import check_address_port
from vquant.library.ctp.win64 import thosttraderapi


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
        self.logger = get_logger('CTPTrader')
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
        self.api.ReqOrderInsert(OrderInsertField(self.broker_id, self.investor_id, exchange_id, instrument_id, offset_flag, direction, price, volume).field, self.request_id)

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
