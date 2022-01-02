class Cerebro(object):
    def __init__(self, broker):
        self.datas = list()
        self.strategies = list()
        self.broker = broker

    def add_data(self, data):
        self.datas.append(data)

    def add_strategy(self, strategy):
        self.strategies.append(strategy(self))

    def run(self):
        pass
