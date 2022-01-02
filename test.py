# import empyrical
# import numpy as np
# import pandas as pd
#
# def sharpe_ratio(num_array)
# np.random.seed(0)
# # Simulate cumulative returns of 100 days
# N = 100
# D = pd.DataFrame(np.random.normal(size=N))
# R = D.cumsum()
# # Calcute returns ratio
# r = (R - R.shift(1))/R.shift(1)
# sr = r.mean()/r.std() * np.sqrt(252)
# print("sharpe ratio =", sr)
#
# import backtrader as bt
#
# class TestStrategy(bt.Strategy):
#     def __init__(self):
#         self.ma5 = bt.indicators.EMA(self.data, period=5)
#         self.ma30 = bt.indicators.EMA(self.data, period=30)

# from brokers.ctpbroker.utils.server_check import check_address_port
#
# print(check_address_port('tcp://218.202.237.33:10203'))

import pandas
#
r = pandas.DataFrame(columns=['a'])
r = r.append([{'a': 1}], ignore_index=True)
r = r.append([{'a': 2}], ignore_index=True)
r = r.append([{'a': 3}], ignore_index=True)
print(r['a'].values, type(r.a.values))
# print(r.a.values[-1])
# getattr(r, 'a').values
# from datetime import datetime
# r = datetime.strptime('20181113', '%Y%m%d')
# print(r)

r = 0.02
m = 5

