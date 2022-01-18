from datetime import datetime
from vquant.utils import exception_catcher
from vquant.utils.logger import get_logger
from server_check import check_address_port
from fields import QryTradingAccountField, QryInvestorPositionField, OrderInsertField, QrySettlementInfoField, SettlementInfoConfirmField, AuthenticateField, UserLoginField
from vquant.library.ctp.win64 import thosttraderapi


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

    def create_order(self, order_ref, exchange_id, instrument_id, offset_flag, direction, price, volume):
        self.api.ReqOrderInsert(OrderInsertField(order_ref, self.broker_id, self.investor_id, exchange_id, instrument_id, offset_flag, direction, price, volume).field, self.request_id)

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
        dt = datetime.strptime(pOrder.TradingDay + pOrder.UpdateTime, '%Y%m%d%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        self.broker.on_order(oid=pOrder.ExchangeID + pOrder.OrderSysID, datetime=dt, symbol=pOrder.InstrumentID, order_ref=pOrder.OrderRef, order_sys_id=pOrder.OrderSysID, exchange_id=pOrder.ExchangeID, side=pOrder.Direction, price=pOrder.LimitPrice, volume=pOrder.VolumeTotalOriginal, status=pOrder.OrderStatus)

    @exception_catcher
    def OnRtnTrade(self, pTrade: thosttraderapi.CThostFtdcTradeField):
        if not pTrade:
            return
        dt = datetime.strptime(pTrade.TradeDate + pTrade.TradeTime, '%Y%m%d%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        self.broker.on_trade(tid=pTrade.ExchangeID + pTrade.TradeID, datetime=dt, trade_id=pTrade.TradeID, order_id=pTrade.ExchangeID + pTrade.OrderSysID, symbol=pTrade.InstrumentID, exchange_id=pTrade.ExchangeID, flag=pTrade.OffsetFlag, side=pTrade.Direction, price=pTrade.Price, volume=pTrade.Volume)

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
