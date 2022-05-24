import pandas
from datetime import datetime


class DateFeed(object):
    def __init__(self):
        self.datas = dict()
        self.datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def add_data(self, symbol, data: pandas.DataFrame):
        self.datas[symbol] = data
        self.datetime = data.iloc[0].datetime

    def push(self, callback):
        for row in self.datas[0].itertuples():
            self.datetime = row.datetime
            callback()
