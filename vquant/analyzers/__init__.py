import pandas
import empyrical


class Analyzer(object):
    def __init__(self, values):
        self.values = values
        self.values['date'] = pandas.to_datetime(self.values['datetime'])
        self.values.set_index('date', inplace=True)
        self.values = self.values.resample('1D').agg({'value': 'last', 'benchmark_value': 'last'}).bfill()
        self.values.loc[:, 'datetime'] = self.values.index.strftime('%Y-%m-%d').tolist()
        self.returns = pandas.Series(index=self.values.index, data=(self.values['value'] - self.values['value'].shift(1)) / self.values['value'].shift(1))
        self.benchmark_returns = pandas.Series(index=self.values.index, data=(self.values['benchmark_value'] - self.values['benchmark_value'].shift(1)) / self.values['benchmark_value'].shift(1))

    def results(self):
        return {
            'annual_return': empyrical.annual_return(self.returns),
            'benchmark_annual_return': empyrical.annual_return(self.benchmark_returns),
            'annual_volatility': empyrical.annual_volatility(self.returns, period='daily'),
            'calmar_ratio': empyrical.calmar_ratio(self.returns),
            'max_drawdown': empyrical.max_drawdown(self.returns),
            'omega_ratio': empyrical.omega_ratio(self.returns),
            'sharpe_ratio': empyrical.sharpe_ratio(self.returns),
            'sortino_ratio': empyrical.sortino_ratio(self.returns),
            'downside_risk': empyrical.downside_risk(self.returns),
            'tail_ratio': empyrical.tail_ratio(self.returns),
            'alpha': empyrical.alpha(self.returns, factor_returns=self.benchmark_returns),
            'bate': empyrical.beta(self.returns, factor_returns=self.benchmark_returns),
            'values': self.values.to_dict(orient='records'),
        }
