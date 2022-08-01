import pandas
from datetime import timedelta


class DateFeed(object):
    def __init__(self):
        self.dataline = dict()
        self.datetime = pandas.Timestamp.now()
        self.datetime = self.datetime - timedelta(seconds=self.datetime.second, microseconds=self.datetime.microsecond)
        self.deadline = pandas.Timestamp.now()
        self.interval = timedelta(minutes=1)

    def read_csv(self, path, symbol, interval: timedelta):
        data = pandas.read_csv(path, dtype=dict(datetime=str, open=float, high=float, low=float, close=float, volume=float))
        data['datetime'] = pandas.to_datetime(data['datetime'])
        data.set_index(data['datetime'], inplace=True)
        if symbol not in self.dataline:
            self.dataline[symbol] = dict()
        self.dataline[symbol].update({
            interval: data
        })

    def feed_to(self, callback):
        while self.datetime < self.deadline:
            message = dict()
            for symbol, data in self.dataline.items():
                for interval in data:
                    if self.datetime in data[interval].index:
                        if symbol not in message:
                            message[symbol] = dict()
                        message[symbol].update({
                            interval: data[interval].loc[self.datetime]
                        })
            if message:
                callback(message)
            self.datetime += self.interval


__all__ = [DateFeed, ]
