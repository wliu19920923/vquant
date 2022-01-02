from order import Order


class Position(object):
    Long, Short = range(2)
    Directions = ['Long', 'Short']

    def __init__(self, broker):
        self.broker = broker

    @property
    def positions(self):
        return self.broker.store.positions

    def on_trade(self, trade):
        if trade['flag'] == Order.Open:
            direction = Position.Long if trade['side'] == Order.Buy else Position.Short
            record = self.positions.loc[(self.positions['symbol'] == trade['symbol']) & (self.positions['direction'] == direction)]
            if record.index:
                position = record.to_dict(orient='records')[0]
                position['cost'] += trade['cost']
                position['volume'] += trade['volume']
                position['margin'] += trade['margin']
            else:
                position = dict(symbol=trade['symbol'], cost=trade['cost'], direction=direction, volume=trade['direction'], margin=trade['margin'], profit=0)
        else:
            direction = Position.Short if trade['side'] == Order.Buy else Position.Long
            record = self.positions.loc[(self.positions['symbol'] == trade['symbol']) & (self.positions['direction'] == direction)]
            position = record.to_dict(orient='records')[0]
            position['cost'] -= position['cost'] / position['volume'] * trade['volume']
            position['volume'] -= trade['volume']
            position['margin'] -= position['margin'] / position['volume'] * trade['volume']
        self.broker.on_position(position)
