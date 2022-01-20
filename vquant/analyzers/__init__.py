import empyrical
import pandas
# import pyfolio
# from matplotlib import pyplot


class Analyzer(object):
    def __init__(self, broker):
        self.broker = broker
        self.broker.store.values['date'] = pandas.to_datetime(self.broker.store.values['datetime'])
        self.broker.store.values.set_index('date', inplace=True)
        self.broker.store.values = self.broker.store.values.resample('1D').agg({'value': 'last', 'benchmark_value': 'last'}).bfill()
        self.broker.store.values.loc[:, 'datetime'] = self.broker.store.values.index.strftime('%Y-%m-%d').tolist()
        self.returns = pandas.Series(
            index=self.broker.store.values.index,
            data=(self.broker.store.values['value'] - self.broker.store.values['value'].shift(1)) / self.broker.store.values['value'].shift(1)
        )
        self.benchmark_returns = pandas.Series(
            index=self.broker.store.values.index,
            data=(self.broker.store.values['benchmark_value'] - self.broker.store.values['benchmark_value'].shift(1)) / self.broker.store.values['benchmark_value'].shift(1)
        )

    @property
    def results(self):
        profit = self.broker.value - self.broker.init_cash
        loss = self.broker.store.trades.loc[self.broker.store.trades['profit'] < 0]['profit'].sum()
        loss = abs(loss)
        return {
            'init_cash': self.broker.init_cash,
            'value': self.broker.value,
            'profit': profit,
            'signals': self.broker.store.trades.shape[0],
            'loss': loss,
            'profit_factor': profit / loss if loss else profit,
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
            'r_squared': empyrical.stability_of_timeseries(self.returns),  # r平方
            'values': self.broker.store.values.to_dict(orient='records'),  # 日收益曲线
            'trades': self.broker.store.trades.to_dict(orient='records')
        }

    # def show(self):
    #     pyfolio.create_returns_tear_sheet(self.returns, self.benchmark_returns)
    #     pyplot.show()
