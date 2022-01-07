import talib


class Indicator(object):
    def __init__(self, data):
        self.__data = data

    def cci(self, period):
        # period: 8, 18, 28, 60
        self.__data.loc[:, 'cci%d' % period] = talib.CCI(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def stddev(self, period):
        # period: 5, 20
        self.__data.loc[:, 'stddev%d' % period] = talib.STDDEV(self.__data.close.values, timeperiod=period, nbdev=1).tolist()
        return self.__data

    def var(self, period):
        # period: 5, 20
        self.__data.loc[:, 'var%d' % period] = talib.VAR(self.__data.close.values, timeperiod=period, nbdev=1).tolist()
        return self.__data

    def bolling(self, period):
        bolling = talib.BBANDS(self.__data.close.values, timeperiod=period, nbdevup=2, nbdevdn=2, matype=0)
        self.__data.loc[:, 'bolling_up%d' % period] = bolling[0].tolist()
        self.__data.loc[:, 'bolling_mb%d' % period] = bolling[1].tolist()
        self.__data.loc[:, 'bolling_lb%d' % period] = bolling[2].tolist()
        return self.__data

    def willr(self, period):
        # period: 14, 28
        self.__data.loc[:, 'willr%d' % period] = talib.WILLR(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def kdj_k(self):
        kdj = talib.STOCH(self.__data.high.values, self.__data.low.values, self.__data.close.values, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        self.__data.loc[:, 'kdj_k'] = kdj[0].tolist()
        self.__data.loc[:, 'kdj_d'] = kdj[1].tolist()
        self.__data.loc[:, 'kdj_j'] = (3 * kdj[0] - 2 * kdj[1]).tolist()
        return self.__data

    def obv(self):
        self.__data.loc[:, 'obv'] = talib.OBV(self.__data.close.values, self.__data.volume.values).tolist()
        return self.__data

    def macd(self):
        macd = talib.MACD(self.__data.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
        self.__data.loc[:, 'macd'] = macd[0].tolist()
        self.__data.loc[:, 'macd_signal'] = macd[1].tolist()
        self.__data.loc[:, 'macd_hist'] = macd[2].tolist()
        return self.__data

    def rsi(self, period):
        # period: 12, 14, 21, 25
        self.__data.loc[:, 'rsi'] = talib.RSI(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def rocp(self, period):
        # period: 1, 2, 3, 4, 5, 21, 63, 125, 250
        self.__data.loc[:, 'rocp'] = talib.ROCP(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def ma(self, period):
        # period: 5, 10, 20, 60, 120, 250
        self.__data.loc[:, 'ma%d' % period] = talib.MA(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def sma(self, period):
        # period: 10, 20, 30, 50
        self.__data.loc[:, 'sma%d' % period] = talib.SMA(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def ema(self, period):
        # period: 5, 10, 12, 20, 26, 50, 100, 200
        self.__data.loc[:, 'ema%d' % period] = talib.EMA(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def trange(self):
        self.__data.loc[:, 'trange'] = talib.TRANGE(self.__data.high.values, self.__data.low.values, self.__data.close.values).tolist()
        return self.__data

    def atr(self):
        self.__data.loc[:, 'atr'] = talib.ATR(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=14).tolist()
        return self.__data

    def natr(self):
        self.__data.loc[:, 'natr'] = talib.NATR(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=14).tolist()
        return self.__data

    def plus_di(self, period):
        # period: 6, 14
        self.__data.loc[:, 'plus_di%d' % period] = talib.PLUS_DI(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def minus_di(self, period):
        # period: 6, 14
        self.__data.loc[:, 'minus_di%d' % period] = talib.MINUS_DI(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def dx(self, period):
        # period: 6, 14
        self.__data.loc[:, 'dx%d' % period] = talib.DX(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def adx(self, period):
        # period: 6, 14
        self.__data.loc[:, 'adx%d' % period] = talib.ADX(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def adxr(self, period):
        # period: 6, 14
        self.__data.loc[:, 'adxr%d' % period] = talib.ADXR(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def trix(self, period):
        # period: 12, 30
        self.__data.loc[:, 'trix%d' % period] = talib.TRIX(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def slope(self, period):
        # period: 8, 14, 28, 60, 120
        self.__data.loc[:, 'slope%d' % period] = talib.LINEARREG_SLOPE(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def angle(self, period):
        # period: 8, 14, 28, 60, 120
        self.__data.loc[:, 'angle%d' % period] = talib.LINEARREG_ANGLE(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def intercept(self, period):
        # period: 8, 14, 28, 60, 120
        self.__data.loc[:, 'intercept%d' % period] = talib.LINEARREG_INTERCEPT(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def tsf(self, period):
        # period: 8, 14
        self.__data.loc[:, 'tsf%d' % period] = talib.TSF(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def apo(self):
        self.__data.loc[:, 'apo'] = talib.APO(self.__data.close.values, fastperiod=12, slowperiod=26, matype=0).tolist()
        return self.__data

    def aroon(self):
        aroon = talib.AROON(self.__data.high.values, self.__data.low.values, timeperiod=14)
        self.__data.loc[:, 'aroon_down'] = aroon[0].tolist()
        self.__data.loc[:, 'aroon_up'] = aroon[1].tolist()
        return self.__data

    def bop(self):
        self.__data.loc[:, 'bop'] = talib.BOP(self.__data.open.values, self.__data.high.values, self.__data.low.values, self.__data.close.values).tolist()
        return self.__data

    def aroonosc(self, period):
        # period: 8, 14
        self.__data.loc[:, 'aroonosc%d' % period] = talib.AROONOSC(self.__data.high.values, self.__data.low.values, timeperiod=period).tolist()
        return self.__data

    def mfi(self, period):
        # period: 8, 14
        self.__data.loc[:, 'mfi%d' % period] = talib.MFI(self.__data.high.values, self.__data.low.values, self.__data.close.values, self.__data.volume.values, timeperiod=period).tolist()
        return self.__data

    def mom(self, period):
        # period: 10
        self.__data.loc[:, 'mom%d' % period] = talib.MOM(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def ppo(self):
        self.__data.loc[:, 'ppo'] = talib.PPO(self.__data.close.values, fastperiod=12, slowperiod=26, matype=0).tolist()
        return self.__data

    def rocr(self, period):
        # period: 2, 4, 8, 16
        self.__data.loc[:, 'rocr%d' % period] = talib.ROCR(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def stoch_k(self):
        stoch = talib.STOCH(self.__data.high.values, self.__data.low.values, self.__data.close.values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        self.__data.loc[:, 'stoch_k'] = stoch[0].tolist()
        self.__data.loc[:, 'stoch_d'] = stoch[1].tolist()
        return self.__data

    def ultosc(self):
        self.__data.loc[:, 'ultosc'] = talib.ULTOSC(self.__data.high.values, self.__data.low.values, self.__data.close.values, timeperiod1=7, timeperiod2=14, timeperiod3=28).tolist()
        return self.__data

    def trendline(self):
        self.__data.loc[:, 'trendline'] = talib.HT_TRENDLINE(self.__data.close.values).tolist()
        return self.__data

    def sar(self):
        self.__data.loc[:, 'sar'] = talib.SAR(self.__data.high.values, self.__data.low.values, acceleration=0, maximum=0).tolist()
        return self.__data

    def cmo(self, period):
        # period: 14, 28
        self.__data.loc[:, 'cmo%d' % period] = talib.CMO(self.__data.close.values, timeperiod=period).tolist()
        return self.__data

    def ad(self):
        self.__data.loc[:, 'ad'] = talib.AD(self.__data.high.values, self.__data.low.values, self.__data.close.values, self.__data.volume.values).tolist()
        return self.__data

    def adosc(self):
        self.__data.loc[:, 'adosc'] = talib.ADOSC(self.__data.high.values, self.__data.low.values, self.__data.close.values, self.__data.volume.values, fastperiod=3, slowperiod=10).tolist()
        return self.__data

    def dcperiod(self):
        self.__data.loc[:, 'dcperiod'] = talib.HT_DCPERIOD(self.__data.close.values).tolist()
        return self.__data

    def dcphase(self):
        self.__data.loc[:, 'dcphase'] = talib.HT_DCPHASE(self.__data.close.values).tolist()
        return self.__data

    def inphase(self):
        self.__data.loc[:, 'inphase'] = talib.HT_PHASOR(self.__data.close.values)[0].tolist()
        return self.__data

    def quadrature(self):
        self.__data.loc[:, 'quadrature'] = talib.HT_PHASOR(self.__data.close.values)[1].tolist()
        return self.__data

    def sine(self):
        self.__data.loc[:, 'sine'] = talib.HT_SINE(self.__data.close.values)[0].tolist()
        return self.__data

    def leadsine(self):
        self.__data.loc[:, 'leadsine'] = talib.HT_SINE(self.__data.close.values)[1].tolist()
        return self.__data

    def trendmode(self):
        self.__data.loc[:, 'trendmode'] = talib.HT_TRENDMODE(self.__data.close.values).tolist()
        return self.__data

    def beta(self, period):
        # period: 5, 14, 28
        self.__data.loc[:, 'beta%d' % period] = talib.BETA(self.__data.high.values, self.__data.low.values, timeperiod=period).tolist()
        return self.__data

    def correl(self, period):
        # period: 14, 30
        self.__data.loc[:, 'correl%d' % period] = talib.CORREL(self.__data.high.values, self.__data.low.values, timeperiod=period).tolist()
        return self.__data

    def pbx(self, period):
        self.__data.loc[:, 'pbx%d' % period] = ((talib.EMA(self.__data.close.values, timeperiod=period) + talib.MA(self.__data.close.values, timeperiod=period * 2) + talib.MA(self.__data.close.values, timeperiod=period * 4)) / 3).tolist()
        return self.__data
