import talib


class Indicator(object):
    def __init__(self, data):
        self.data = data

    def cci(self, period):
        # period: 8, 18, 28, 60
        self.data.loc[:, 'cci%d' % period] = talib.CCI(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def stddev(self, period):
        # period: 5, 20
        self.data.loc[:, 'stddev%d' % period] = talib.STDDEV(self.data.close.values, timeperiod=period, nbdev=1).tolist()

    def var(self, period):
        # period: 5, 20
        self.data.loc[:, 'var%d' % period] = talib.VAR(self.data.close.values, timeperiod=period, nbdev=1).tolist()

    def bolling(self, period):
        bolling = talib.BBANDS(self.data.close.values, timeperiod=period, nbdevup=2, nbdevdn=2, matype=0)
        self.data.loc[:, 'bolling_up%d' % period] = bolling[0].tolist()
        self.data.loc[:, 'bolling_mb%d' % period] = bolling[1].tolist()
        self.data.loc[:, 'bolling_lb%d' % period] = bolling[2].tolist()

    def willr(self, period):
        # period: 14, 28
        self.data.loc[:, 'willr%d' % period] = talib.WILLR(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def kdj(self):
        kdj = talib.STOCH(self.data.high.values, self.data.low.values, self.data.close.values, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        self.data.loc[:, 'kdj_k'] = kdj[0].tolist()
        self.data.loc[:, 'kdj_d'] = kdj[1].tolist()
        self.data.loc[:, 'kdj_j'] = (3 * kdj[0] - 2 * kdj[1]).tolist()

    def obv(self):
        self.data.loc[:, 'obv'] = talib.OBV(self.data.close.values, self.data.volume.values).tolist()

    def macd(self):
        macd = talib.MACD(self.data.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
        self.data.loc[:, 'macd'] = macd[0].tolist()
        self.data.loc[:, 'macd_signal'] = macd[1].tolist()
        self.data.loc[:, 'macd_hist'] = macd[2].tolist()

    def rsi(self, period):
        # period: 12, 14, 21, 25
        self.data.loc[:, 'rsi%d' % period] = talib.RSI(self.data.close.values, timeperiod=period).tolist()

    def rocp(self, period):
        # period: 1, 2, 3, 4, 5, 21, 63, 125, 250
        self.data.loc[:, 'rocp%d' % period] = talib.ROCP(self.data.close.values, timeperiod=period).tolist()

    def ma(self, period):
        # period: 5, 10, 20, 60, 120, 250
        self.data.loc[:, 'ma%d' % period] = talib.MA(self.data.close.values, timeperiod=period).tolist()

    def sma(self, period):
        # period: 10, 20, 30, 50
        self.data.loc[:, 'sma%d' % period] = talib.SMA(self.data.close.values, timeperiod=period).tolist()

    def ema(self, period):
        # period: 5, 10, 12, 20, 26, 50, 100, 200
        self.data.loc[:, 'ema%d' % period] = talib.EMA(self.data.close.values, timeperiod=period).tolist()

    def trange(self):
        self.data.loc[:, 'trange'] = talib.TRANGE(self.data.high.values, self.data.low.values, self.data.close.values).tolist()

    def atr(self, timeperiod=14):
        self.data.loc[:, 'atr'] = talib.ATR(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=timeperiod).tolist()

    def natr(self, timeperiod=14):
        self.data.loc[:, 'natr'] = talib.NATR(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=timeperiod).tolist()

    def plus_di(self, period):
        # period: 6, 14
        self.data.loc[:, 'plus_di%d' % period] = talib.PLUS_DI(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def minus_di(self, period):
        # period: 6, 14
        self.data.loc[:, 'minus_di%d' % period] = talib.MINUS_DI(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def dx(self, period):
        # period: 6, 14
        self.data.loc[:, 'dx%d' % period] = talib.DX(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def adx(self, period):
        # period: 6, 14
        self.data.loc[:, 'adx%d' % period] = talib.ADX(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def adxr(self, period):
        # period: 6, 14
        self.data.loc[:, 'adxr%d' % period] = talib.ADXR(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod=period).tolist()

    def trix(self, period):
        # period: 12, 30
        self.data.loc[:, 'trix%d' % period] = talib.TRIX(self.data.close.values, timeperiod=period).tolist()

    def slope(self, period):
        # period: 8, 14, 28, 60, 120
        self.data.loc[:, 'slope%d' % period] = talib.LINEARREG_SLOPE(self.data.close.values, timeperiod=period).tolist()

    def angle(self, period):
        # period: 8, 14, 28, 60, 120
        self.data.loc[:, 'angle%d' % period] = talib.LINEARREG_ANGLE(self.data.close.values, timeperiod=period).tolist()

    def intercept(self, period):
        # period: 8, 14, 28, 60, 120
        self.data.loc[:, 'intercept%d' % period] = talib.LINEARREG_INTERCEPT(self.data.close.values, timeperiod=period).tolist()

    def tsf(self, period):
        # period: 8, 14
        self.data.loc[:, 'tsf%d' % period] = talib.TSF(self.data.close.values, timeperiod=period).tolist()

    def apo(self):
        self.data.loc[:, 'apo'] = talib.APO(self.data.close.values, fastperiod=12, slowperiod=26, matype=0).tolist()

    def aroon(self):
        aroon = talib.AROON(self.data.high.values, self.data.low.values, timeperiod=14)
        self.data.loc[:, 'aroon_down'] = aroon[0].tolist()
        self.data.loc[:, 'aroon_up'] = aroon[1].tolist()

    def bop(self):
        self.data.loc[:, 'bop'] = talib.BOP(self.data.open.values, self.data.high.values, self.data.low.values, self.data.close.values).tolist()

    def aroonosc(self, period):
        # period: 8, 14
        self.data.loc[:, 'aroonosc%d' % period] = talib.AROONOSC(self.data.high.values, self.data.low.values, timeperiod=period).tolist()

    def mfi(self, period):
        # period: 8, 14
        self.data.loc[:, 'mfi%d' % period] = talib.MFI(self.data.high.values, self.data.low.values, self.data.close.values, self.data.volume.values, timeperiod=period).tolist()

    def mom(self, period):
        # period: 10
        self.data.loc[:, 'mom%d' % period] = talib.MOM(self.data.close.values, timeperiod=period).tolist()

    def ppo(self):
        self.data.loc[:, 'ppo'] = talib.PPO(self.data.close.values, fastperiod=12, slowperiod=26, matype=0).tolist()

    def rocr(self, period):
        # period: 2, 4, 8, 16
        self.data.loc[:, 'rocr%d' % period] = talib.ROCR(self.data.close.values, timeperiod=period).tolist()

    def stoch_k(self):
        stoch = talib.STOCH(self.data.high.values, self.data.low.values, self.data.close.values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        self.data.loc[:, 'stoch_k'] = stoch[0].tolist()
        self.data.loc[:, 'stoch_d'] = stoch[1].tolist()

    def ultosc(self):
        self.data.loc[:, 'ultosc'] = talib.ULTOSC(self.data.high.values, self.data.low.values, self.data.close.values, timeperiod1=7, timeperiod2=14, timeperiod3=28).tolist()

    def trendline(self):
        self.data.loc[:, 'trendline'] = talib.HT_TRENDLINE(self.data.close.values).tolist()

    def sar(self):
        self.data.loc[:, 'sar'] = talib.SAR(self.data.high.values, self.data.low.values, acceleration=0, maximum=0).tolist()

    def cmo(self, period):
        # period: 14, 28
        self.data.loc[:, 'cmo%d' % period] = talib.CMO(self.data.close.values, timeperiod=period).tolist()

    def ad(self):
        self.data.loc[:, 'ad'] = talib.AD(self.data.high.values, self.data.low.values, self.data.close.values, self.data.volume.values).tolist()

    def adosc(self):
        self.data.loc[:, 'adosc'] = talib.ADOSC(self.data.high.values, self.data.low.values, self.data.close.values, self.data.volume.values, fastperiod=3, slowperiod=10).tolist()

    def dcperiod(self):
        self.data.loc[:, 'dcperiod'] = talib.HT_DCPERIOD(self.data.close.values).tolist()

    def dcphase(self):
        self.data.loc[:, 'dcphase'] = talib.HT_DCPHASE(self.data.close.values).tolist()

    def inphase(self):
        self.data.loc[:, 'inphase'] = talib.HT_PHASOR(self.data.close.values)[0].tolist()

    def quadrature(self):
        self.data.loc[:, 'quadrature'] = talib.HT_PHASOR(self.data.close.values)[1].tolist()

    def sine(self):
        self.data.loc[:, 'sine'] = talib.HT_SINE(self.data.close.values)[0].tolist()

    def leadsine(self):
        self.data.loc[:, 'leadsine'] = talib.HT_SINE(self.data.close.values)[1].tolist()

    def trendmode(self):
        self.data.loc[:, 'trendmode'] = talib.HT_TRENDMODE(self.data.close.values).tolist()

    def beta(self, period):
        # period: 5, 14, 28
        self.data.loc[:, 'beta%d' % period] = talib.BETA(self.data.high.values, self.data.low.values, timeperiod=period).tolist()

    def correl(self, period):
        # period: 14, 30
        self.data.loc[:, 'correl%d' % period] = talib.CORREL(self.data.high.values, self.data.low.values, timeperiod=period).tolist()

    def pbx(self, period):
        self.data.loc[:, 'pbx%d' % period] = ((talib.EMA(self.data.close.values, timeperiod=period) + talib.MA(self.data.close.values, timeperiod=period * 2) + talib.MA(self.data.close.values,
                                                                                                                                                                         timeperiod=period * 4)) / 3).tolist()
