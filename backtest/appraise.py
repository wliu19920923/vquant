import math
import numpy


class Appraise(object):
    def __init__(self, history, **kwargs):
        self.history = history
        self.execution_days = math.ceil((self.history[-1]['t'] - self.history[0]['t']) / 86400)
        self.risk_free_profit_rate = 'risk_free_profit_rate' in kwargs and kwargs['risk_free_profit_rate'] or 0.038
        self.annualized_trading_days = 'annualized_trading_days' in kwargs and kwargs['annualized_trading_days'] or 365

    @staticmethod
    def _convert_float(value):
        ret = 0 if math.isnan(value) or math.isinf(value) else value
        return round(ret, 2)

    def alpha(self):
        beta = self.beta()
        ret = (self.history[-1]['profit'] - self.risk_free_profit_rate) - beta * (self.history[-1]['benchmark_profit'] - self.risk_free_profit_rate)
        return self._convert_float(ret)

    def beta(self):
        profit_list = list()
        benchmark_profit_list = list()
        for i in self.history:
            profit_list.append(i['profit'])
            benchmark_profit_list.append(i['benchmark_profit'])
        profit_cov = numpy.cov(profit_list, benchmark_profit_list)
        ret = profit_cov[0, 1] / profit_cov[0, 0] if profit_cov[0, 0] else 0
        return self._convert_float(ret)

    def annualized_profit_rate(self):
        ret = (self.history[-1]['fund'] - self.history[0]['fund']) / self.history[0]['fund'] / self.execution_days * self.annualized_trading_days
        return self._convert_float(ret)

    def benchmark_annualized_profit_rate(self):
        ret = (self.history[-1]['price'] - self.history[0]['price']) / self.history[0]['price'] / self.execution_days * self.annualized_trading_days
        return self._convert_float(ret)

    def information_ratio(self):
        data = [i['profit'] - i['benchmark_profit'] for i in self.history]
        annualized_profit_rate = self.annualized_profit_rate()
        benchmark_annualized_profit_rate = self.benchmark_annualized_profit_rate()
        std_difference = numpy.std(data)
        ret = (annualized_profit_rate - benchmark_annualized_profit_rate) / std_difference
        return self._convert_float(ret)

    def maximum_retreat(self):
        ret = 0
        for i in range(1, len(self.history)):
            max_fund = max([self.history[j]['fund'] for j in range(i)])
            retreat = (max_fund - self.history[i]['fund']) / max_fund
            ret = retreat > ret and retreat or ret
        return self._convert_float(ret)

    def profit_loss_ratio(self):
        total_loss = 0
        total_profit = 0
        for i in self.history:
            if i['profit'] < 0:
                total_loss += i['profit']
            else:
                total_profit += i['profit']
        ret = abs(total_profit / total_loss) if total_loss else 0
        return self._convert_float(ret)

    def return_volatility(self):
        ret = numpy.std([i['profit'] for i in self.history])
        return self._convert_float(ret)

    def sharpe_ratio(self):
        annualized_profit_rate = self.annualized_profit_rate()
        return_volatility = self.return_volatility()
        ret = (annualized_profit_rate - self.risk_free_profit_rate) / return_volatility if return_volatility else 0
        return self._convert_float(ret)

    def result(self):
        return {
            'alpha': self.alpha(),
            'beta': self.beta(),
            'annualized_profit_rate': self.annualized_profit_rate(),
            'benchmark_annualized_profit_rate': self.benchmark_annualized_profit_rate(),
            'information_ratio': self.information_ratio(),
            'maximum_retreat': self.maximum_retreat(),
            'profit_loss_ratio': self.profit_loss_ratio(),
            'return_volatility': self.return_volatility(),
            'sharpe_ratio': self.sharpe_ratio()
        }
