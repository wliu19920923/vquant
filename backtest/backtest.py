import logging
from appraise import Appraise


class BackTest(object):
    def __init__(self, data, fund=1000000, investment=10000, is_spot=True, **kwargs):
        self.data = data  # k线数据
        self.profit = 0
        self.logger = logging.getLogger('BackTest')
        self.logger.setLevel('logger_level' in kwargs and kwargs['logger_level'] or logging.INFO)
        self.orders = list()  # 订单
        self.trades = list()  # 交易记录
        self.history = list()  # 交易日志
        self.is_spot = is_spot
        self.investment = investment  # 开仓投入资金
        self.initial_fund = fund  # 初始资金
        self.current_fund = fund  # 当前资金
        self.min_float_profit = 0
        self.max_float_profit = 0
        self.kwargs = kwargs

    def open(self, t, side, price, amount):
        volume = price * amount
        if side == BID:
            self.current_fund -= amount
            self.orders.append({'t': t, 'side': BID, 'price': price, 'amount': amount, 'volume': volume})
            self.trades.append({'t': t, 'side': BID, 'price': price, 'amount': amount, 'volume': volume, 'operate': 'open'})
        else:
            if not self.is_spot:
                self.orders.append({'t': t, 'side': ASK, 'price': price, 'amount': amount, 'volume': volume})
                self.trades.append({'t': t, 'side': ASK, 'price': price, 'amount': amount, 'volume': volume, 'operate': 'open'})

    def close(self, t, side, price):
        profit = 0
        if side == BID:
            for order in self.orders:
                if order['side'] == ASK:
                    profit += (order['price'] - price) * order['amount']
                    self.trades.append({'t': t, 'side': BID, 'price': price, 'amount': order['amount'], 'volume': price * order['amount'], 'operate': 'close'})
                    self.orders.remove(order)
        else:
            for order in self.orders:
                if order['side'] == BID:
                    profit += (price - order['price']) * order['amount']
                    self.trades.append({'t': t, 'side': ASK, 'price': price, 'amount': order['amount'], 'volume': price * order['amount'], 'operate': 'close'})
                    self.orders.remove(order)
        self.profit += profit
        self.current_fund += profit

    def holding(self, price):
        volume = 0
        for order in self.orders:
            if order['side'] == BID:
                volume += price * order['amount']
            else:
                volume += (order['price'] - price) * order['amount']
        return volume

    def float_profit(self, price):
        holding_amount = sum(order['amount'] for order in self.orders)
        holding_volume = sum(order['volume'] for order in self.orders)
        floating_volume = price * holding_amount
        return holding_volume and (floating_volume - holding_volume) / holding_volume or 0

    def benchmark_profit(self, price):
        return self.history and (price - self.history[0]['price']) / self.history[0]['price'] or 0

    def statistics(self, t, price):
        return {
            't': t,
            'price': price,
            'profit': self.profit,
            'float_profit': self.float_profit(price),
            'benchmark_profit': self.benchmark_profit(price),
            'fund': self.current_fund + self.holding(price)
        }

    def resolve(self, data, strategy):
        t = data[-1]['t']
        price = data[-1]['c']
        history = self.statistics(t, price)
        self.history.append(history)
        side = strategy(data, orders=self.orders, history=self.history, **self.kwargs).resolve()
        if side:
            self.close(t, side, price)
            amount = self.current_fund > self.investment and self.investment / price or self.current_fund / price
            if amount > 0:
                self.open(t, side, price, amount)
        self.history[-1]['profit'] = self.profit

    def run(self, strategy):
        for i in range(1, len(self.data)):
            data = self.data[0:i]
            self.resolve(data, strategy)
        return Appraise(self.history).result()


if __name__ == '__main__':
    import requests
    from strategy import GridArbitrage

    response = requests.get('http://151.106.35.109:16006/market/kline?exchange=Huobi&base=btc&quote=usdt&period=1m')
    print(response.text)
    response = response.json()
    bk = BackTest(response['data'], grid_count=7, grid_height=0.01, target_back=0, target_rate=0.0003, supplement_back=0)
    r = bk.run(GridArbitrage)
    print(bk.trades)
    print(bk.history)
    print(r)
