import empyrical
import pandas


class Analyzer(object):
    def __init__(self, broker):
        self.broker = broker
        self.broker.NetValue.Store['date'] = pandas.to_datetime(self.broker.NetValue.Store['datetime'])
        self.broker.NetValue.Store.set_index('date', inplace=True)
        self.broker.NetValue.Store = self.broker.NetValue.Store.resample('1D').agg({'value': 'last', 'benchmark_value': 'last'}).bfill()
        self.broker.NetValue.Store.loc[:, 'datetime'] = self.broker.NetValue.Store.index.strftime('%Y-%m-%d').tolist()
        self.returns = pandas.Series(
            index=self.broker.NetValue.Store.index,
            data=(self.broker.NetValue.Store['value'] - self.broker.NetValue.Store['value'].shift(1)) / self.broker.NetValue.Store['value'].shift(1)
        )
        self.benchmark_returns = pandas.Series(
            index=self.broker.NetValue.Store.index,
            data=(self.broker.NetValue.Store['benchmark_value'] - self.broker.NetValue.Store['benchmark_value'].shift(1)) / self.broker.NetValue.Store['benchmark_value'].shift(1)
        )

    @property
    def trades(self):
        return self.broker.Trade.Store.to_dict(orient='records')

    @property
    def values(self):
        return self.broker.NetValue.Store.to_dict(orient='records')

    def run(self):
        return {
            'capital': self.broker.capital,
            'value': self.broker.value,
            'profit': self.broker.value - self.broker.capital,
            'signals': self.broker.Trade.Store.shape[0],
            'annual_return': empyrical.annual_return(self.returns),  # 年华收益率
            'benchmark_annual_return': empyrical.annual_return(self.benchmark_returns),  # 标准年华收益率
            'annual_volatility': empyrical.annual_volatility(self.returns),  # 年华波动率
            'cagr': empyrical.cagr(self.returns),  # 年复合增长率
            'calmar_ratio': empyrical.calmar_ratio(self.returns),  # 卡玛率
            'max_drawdown': empyrical.max_drawdown(self.returns),  # 最大回撤
            'omega_ratio': empyrical.omega_ratio(self.returns),  # 欧米茄率
            'sharpe_ratio': empyrical.sharpe_ratio(self.returns),  # 夏普率
            'sortino_ratio': empyrical.sortino_ratio(self.returns),  # 索蒂诺比率
            'downside_risk': empyrical.downside_risk(self.returns),  # 下行风险
            'tail_ratio': empyrical.tail_ratio(self.returns),  # 尾比
            'alpha': empyrical.alpha(self.returns, factor_returns=self.benchmark_returns),  # 阿尔法
            'bate': empyrical.beta(self.returns, factor_returns=self.benchmark_returns),  # 贝塔
            'r_squared': empyrical.stability_of_timeseries(self.returns)  # r平方
        }
