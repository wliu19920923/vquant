import numpy
import pandas
import talib

INDICATOR_MAP = [
    'open', 'high', 'low', 'close', 'volume',
    'cci8', 'cci18', 'cci28', 'cci60',
    'stddev5', 'stddev8', 'stddev18', 'stddev20', 'stddev28',
    'var5', 'var8', 'var18', 'var20', 'var28',
    'bolling-ub', 'bolling-mb', 'bolling-lb',
    'willr14', 'willr20', 'willr28',
    'kdj-k', 'kdj-d', 'kdj-j',
    'obv', 'macd', 'macdsignal', 'macddist',
    'rsi8', 'rsi12', 'rsi14', 'rsi21', 'rsi25', 'rsi28', 'rsi60',
    'rocp1', 'rocp2', 'rocp3', 'rocp4', 'rocp5', 'rocp21', 'rocp63', 'rocp125', 'rocp250',
    'ma5', 'ma10', 'ma20', 'ma60', 'ma120', 'ma250',
    'sma10', 'sma20', 'sma30', 'sma50',
    'ema5', 'ema9', 'ema10', 'ema12', 'ema20', 'ema21', 'ema26', 'ema28', 'ema50', 'ema60', 'ema100', 'ema200',
    'trange', 'atr14', 'natr14', '+di6', '+di14', '-di6', '-di14',
    'dx6', 'dx14', 'adx6', 'adx14', 'adxr6', 'adxr14', 'trix12', 'trix30',
    'slope8', 'slope14', 'slope28', 'slope60', 'slope120',
    'angle8', 'angle14', 'angle28', 'angle60', 'angle120',
    'intercept8', 'intercept14', 'intercept28', 'intercept60', 'intercept120',
    'tsf8', 'tsf14', 'apo', 'aroondown', 'aroonup', 'bop', 'aroonosc8', 'aroonosc16',
    'mfi8', 'mfi14', 'mom10', 'ppo',
    'rocr2', 'rocr4', 'rocr8', 'rocr16',
    'stoch-k', 'stoch-d', 'ultosc', 'trendline', 'sar',
    'cmo-14', 'cmo-28', 'ad', 'adosc', 'dcperiod', 'dcphase', 'inphase', 'quadrature', 'sine', 'leadsine', 'trendmode',
    'beta-5', 'beta-14', 'beta-28', 'correl-14', 'correl-30'
]


class Indicator(object):
    def __init__(self, data: pandas.DataFrame):
        self.low = data.low.values()
        self.open = data.open.values()
        self.high = data.open.values()
        self.close = data.open.values()
        self.volume = data.open.values()
        self.timestamp = numpy.array(data['datetime'])

    def cci(self, time_period):
        # time_period: 8, 18, 28, 60
        return talib.CCI(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def stddev(self, time_period):
        # time_period: 5, 20
        return talib.STDDEV(self.close, timeperiod=time_period, nbdev=1).tolist()

    def var(self, time_period):
        # time_period: 5, 20
        return talib.VAR(self.close, timeperiod=time_period, nbdev=1).tolist()

    def bolling_up(self):
        return talib.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[0].tolist()

    def bolling_mb(self):
        return talib.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[1].tolist()

    def bolling_lb(self):
        return talib.BBANDS(self.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[2].tolist()

    def willr(self, time_period):
        # time_period: 14, 28
        return talib.WILLR(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def kdj_k(self):
        return talib.STOCH(self.high, self.low, self.close, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)[0].tolist()

    def kdj_d(self):
        return talib.STOCH(self.high, self.low, self.close, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)[1].tolist()

    def kdj_j(self):
        return (3 * talib.STOCH(self.high, self.low, self.close, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)[0] - 2 * talib.STOCH(self.high, self.low, self.close, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)[1]).tolist()

    def obv(self):
        return talib.OBV(self.close, self.volume).tolist()

    def macd(self):
        return talib.MACD(self.close, fastperiod=12, slowperiod=26, signalperiod=9)[0].tolist()

    def macd_signal(self):
        return talib.MACD(self.close, fastperiod=12, slowperiod=26, signalperiod=9)[1].tolist()

    def macd_hist(self):
        return talib.MACD(self.close, fastperiod=12, slowperiod=26, signalperiod=9)[2].tolist()

    def rsi(self, time_period):
        # time_period: 12, 14, 21, 25
        return talib.RSI(self.close, timeperiod=time_period).tolist()

    def rocp(self, time_period):
        # time_period: 1, 2, 3, 4, 5, 21, 63, 125, 250
        return talib.ROCP(self.close, timeperiod=time_period).tolist()

    def ma(self, time_period):
        # time_period: 5, 10, 20, 60, 120, 250
        return talib.MA(self.close, timeperiod=time_period).tolist()

    def sma(self, time_period):
        # time_period: 10, 20, 30, 50
        return talib.SMA(self.close, timeperiod=time_period).tolist()

    def ema(self, time_period):
        # time_period: 5, 10, 12, 20, 26, 50, 100, 200
        return talib.EMA(self.close, timeperiod=time_period).tolist()

    def trange(self):
        return talib.TRANGE(self.high, self.low, self.close).tolist()

    def atr(self):
        return talib.ATR(self.high, self.low, self.close, timeperiod=14).tolist()

    def natr(self):
        return talib.NATR(self.high, self.low, self.close, timeperiod=14).tolist()

    def plus_di(self, time_period):
        # time_period: 6, 14
        return talib.PLUS_DI(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def minus_di(self, time_period):
        # time_period: 6, 14
        return talib.MINUS_DI(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def dx(self, time_period):
        # time_period: 6, 14
        return talib.DX(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def adx(self, time_period):
        # time_period: 6, 14
        return talib.ADX(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def adxr(self, time_period):
        # time_period: 6, 14
        return talib.ADXR(self.high, self.low, self.close, timeperiod=time_period).tolist()

    def trix(self, time_period):
        # time_period: 12, 30
        return talib.TRIX(self.close, timeperiod=time_period).tolist()

    def slope(self, time_period):
        # time_period: 8, 14, 28, 60, 120
        return talib.LINEARREG_SLOPE(self.close, timeperiod=time_period).tolist()

    def angle(self, time_period):
        # time_period: 8, 14, 28, 60, 120
        return talib.LINEARREG_ANGLE(self.close, timeperiod=time_period).tolist()

    def intercept(self, time_period):
        # time_period: 8, 14, 28, 60, 120
        return talib.LINEARREG_INTERCEPT(self.close, timeperiod=time_period).tolist()

    def tsf(self, time_period):
        # time_period: 8, 14
        return talib.TSF(self.close, timeperiod=time_period).tolist()

    def apo(self):
        return talib.APO(self.close, fastperiod=12, slowperiod=26, matype=0).tolist()

    def aroon_down(self):
        return talib.AROON(self.high, self.low, timeperiod=14)[0].tolist()

    def aroon_up(self):
        return talib.AROON(self.high, self.low, timeperiod=14)[1].tolist()

    def bop(self):
        return talib.BOP(self.open, self.high, self.low, self.close).tolist()

    def aroonosc(self, time_period):
        # time_period: 8, 14
        return talib.AROONOSC(self.high, self.low, timeperiod=time_period).tolist()

    def mfi(self, time_period):
        # time_period: 8, 14
        return talib.MFI(self.high, self.low, self.close, self.volume, timeperiod=time_period).tolist()

    def mom(self, time_period):
        # time_period: 10
        return talib.MOM(self.close, timeperiod=time_period).tolist()

    def ppo(self):
        return talib.PPO(self.close, fastperiod=12, slowperiod=26, matype=0).tolist()

    def rocr(self, time_period):
        # time_period: 2, 4, 8, 16
        return talib.ROCR(self.close, timeperiod=time_period).tolist()

    def stoch_k(self, index):
        return talib.STOCH(self.high, self.low, self.close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)[0].tolist()

    def stoch_d(self, index):
        return talib.STOCH(self.high, self.low, self.close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)[1].tolist()

    def ultosc(self):
        return talib.ULTOSC(self.high, self.low, self.close, timeperiod1=7, timeperiod2=14, timeperiod3=28).tolist()

    def trendline(self):
        return talib.HT_TRENDLINE(self.close).tolist()

    def sar(self):
        return talib.SAR(self.high, self.low, acceleration=0, maximum=0).tolist()

    def cmo(self, time_period):
        # time_period: 14, 28
        return talib.CMO(self.close, timeperiod=time_period).tolist()

    def ad(self):
        return talib.AD(self.high, self.low, self.close, self.volume).tolist()

    def adosc(self):
        return talib.ADOSC(self.high, self.low, self.close, self.volume, fastperiod=3, slowperiod=10).tolist()

    def dcperiod(self):
        return talib.HT_DCPERIOD(self.close).tolist()

    def dcphase(self):
        return talib.HT_DCPHASE(self.close).tolist()

    def inphase(self):
        return talib.HT_PHASOR(self.close)[0].tolist()

    def quadrature(self):
        return talib.HT_PHASOR(self.close)[1].tolist()

    def sine(self):
        return talib.HT_SINE(self.close)[0].tolist()

    def leadsine(self):
        return talib.HT_SINE(self.close)[1].tolist()

    def trendmode(self):
        return talib.HT_TRENDMODE(self.close).tolist()

    def beta(self, time_period):
        # time_period: 5, 14, 28
        return talib.BETA(self.high, self.low, timeperiod=time_period).tolist()

    def correl(self, time_period):
        # time_period: 14, 30
        return talib.CORREL(self.high, self.low, timeperiod=time_period).tolist()

    def pbx(self, time_period):
        return ((talib.EMA(self.close, timeperiod=time_period) + talib.MA(self.close, timeperiod=time_period * 2) + talib.MA(self.close, timeperiod=time_period * 4)) / 3).tolist()
