import pandas

field_types = dict(datetime=str, open=float, high=float, low=float, close=float, volume=float)


class ReadCSV(object):
    def __init__(self, filepath):
        self.data = pandas.read_csv(filepath, dtype=field_types)