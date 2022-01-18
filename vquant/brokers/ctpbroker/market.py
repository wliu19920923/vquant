from server_check import check_address_port
from vquant.utils import exception_catcher
from vquant.utils.logger import get_logger
from vquant.library.ctp.win64 import thostmduserapi


class MarketApi(thostmduserapi.CThostFtdcMdSpi):
    def __init__(self, on_tick):
        thostmduserapi.CThostFtdcMdSpi.__init__(self)
        self.api = thostmduserapi.CThostFtdcMdApi_CreateFtdcMdApi()
        self.logger = get_logger('CTPMarket')
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
