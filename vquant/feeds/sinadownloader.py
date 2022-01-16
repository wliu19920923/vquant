import pandas
import requests


class Sina(object):
    fields = dict(datetime=str, open=float, high=float, low=float, close=float, volume=float)

    def __init__(self, symbol, period):
        """
        :param symbol: RB0 螺纹钢,AG0 白银,AU0 黄金,CU0 沪铜,AL0 沪铝,ZN0 沪锌,PB0 沪铅,RU0 橡胶,FU0 燃油,WR0 线材,A0 大豆,M0 豆粕,Y0 豆油,J0 焦炭,C0 玉米,L0 乙烯,P0 棕油,V0 PVC,RS0 菜籽,RM0 菜粕,FG0 玻璃,CF0 棉花,WS0 强麦,ER0 籼稻,ME0 甲醇,RO0 菜油,TA0 甲酸
        :param period: 5m,15m,30m,60m,day
        """
        self.symbol = symbol
        self.period = period

    def down_min_kline(self):
        url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine%s?symbol=%s' % (self.period, self.symbol)
        response = requests.get(url).json()
        data = pandas.DataFrame(response[::-1], columns=list(self.fields.keys()))
        data.to_csv('../../datas/%s_%s.csv' % (self.symbol, self.period))

    def down_day_kline(self):
        response = requests.get('http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=%s' % self.symbol).json()
        data = pandas.DataFrame(response[::-1], columns=list(self.fields.keys()))
        data.to_csv('../../datas/%s_day.csv' % self.symbol)

    def run(self):
        if self.period not in ('5m', '15m', '30m', '60m'):
            self.down_day_kline()
        else:
            self.down_min_kline()


if __name__ == '__main__':
    Sina('J0', '30m').run()