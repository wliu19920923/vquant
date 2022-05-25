import pandas

field_types = dict(datetime=str, open=float, high=float, low=float, close=float, volume=float)


class ReadCSV(object):
    def __init__(self, filepath):
        self.data = pandas.read_csv(filepath, dtype=field_types, index_col=0)
        self.data['datetime'] = pandas.to_datetime(self.data['datetime'])


c = ReadCSV('../../datas/RB0_30m.csv')
print(c.data)
