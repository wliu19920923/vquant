import pandas
from datetime import timedelta
from pathlib import Path


class DateFeed(object):
    def __init__(self, **kwargs):
        self.datas = dict()
        self.interval = kwargs.get('interval') or timedelta(minutes=1)
        self.datetime = kwargs.get('datetime') or pandas.Timestamp.now()
        self.datetime = self.datetime - timedelta(seconds=self.datetime.second, microseconds=self.datetime.microsecond)

    def read_csv(self, path):
        name = Path(path).stem
        data = pandas.read_csv(path, dtype=dict(datetime=str, open=float, high=float, low=float, close=float, volume=float), index_col=0)
        data['datetime'] = pandas.to_datetime(data['datetime'])
        data.set_index(data['datetime'], inplace=True)
        self.datas[name] = data

    def feed_to(self, callback):
        while self.datetime < pandas.Timestamp.now():
            datas = {key: data.loc[self.datetime] for key, data in self.datas.items() if self.datetime in data.index}
            self.datetime += self.interval
            if not datas:
                continue
            callback(datetime=self.datetime, datas=datas)


if __name__ == '__main__':
    def cb(**kwargs):
        print(kwargs)


    d = DateFeed(interval=timedelta(minutes=30), datetime=pandas.Timestamp(year=2021, month=12, day=29, hour=14, minute=30))
    d.read_csv('../../datas/RB0_30m.csv')
    d.read_csv('../../datas/RB0_day.csv')
    d.feed_to(cb)
