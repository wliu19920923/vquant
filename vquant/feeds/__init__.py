import pandas
from datetime import timedelta
from pathlib import Path


class DateFeed(object):
    def __init__(self):
        self.datas = dict()
        self.interval = timedelta(minutes=1)
        self.datetime = pandas.Timestamp.now()
        self.datetime = self.datetime - timedelta(seconds=self.datetime.second, microseconds=self.datetime.microsecond)

    def read_csv(self, path):
        name = Path(path).stem
        data = pandas.read_csv(path, dtype=dict(datetime=str, open=float, high=float, low=float, close=float, volume=float), index_col=0)
        data['datetime'] = pandas.to_datetime(data['datetime'])
        data.set_index(data['datetime'], inplace=True)
        self.datas[name] = data

    def feed_to(self, callback):
        while self.datetime < pandas.Timestamp.now():
            message = {key: data.loc[self.datetime] for key, data in self.datas.items() if self.datetime in data.index}
            callback(message)
