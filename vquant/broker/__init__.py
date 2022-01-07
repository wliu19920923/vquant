import os
import binascii


class SymbolInfo(object):
    """
        - commission: 每笔手续费
        - margin_rate: 保证金率
        - volume_multiple: 数量乘数
        - target_index: 数据下标
    """

    def __init__(self, commission, margin_rate, volume_multiple, target_index):
        self.commission = commission
        self.margin_rate = margin_rate
        self.volume_multiple = volume_multiple
        self.target_index = target_index


class Order(object):
    """
      Order Flags
      - Open: increase position
      - Close: reduce position
      Order Types
      - Buy: buy
      - Sell: Sell
      Order Status
      - Submitted: sent to the broker and awaiting confirmation
      - Accepted: accepted by the broker
      - Partial: partially executed
      - Completed: fully exexcuted
      - Canceled/Cancelled: canceled by the user
      - Expired: expired
      - Margin: not enough cash to execute the order.
      - Rejected: Rejected by the broker
    """
    Open, Close = range(2)
    Flags = ['Open', 'Close']

    Buy, Sell = range(2)
    Sides = ['Buy', 'Sell']

    Created, Submitted, Accepted, Partial, Completed, Canceled, Expired, Margin, Rejected = range(9)
    Status = [
        'Created', 'Submitted', 'Accepted', 'Partial', 'Completed',
        'Canceled', 'Expired', 'Margin', 'Rejected'
    ]

    def __init__(self, datetime, symbol, flag, side, price, volume, commission, margin, status):
        self.id = binascii.hexlify(os.urandom(12)).decode()
        self.datetime = datetime
        self.symbol = symbol
        self.flag = flag
        self.side = side
        self.price = price
        self.volume = volume
        self.commission = commission
        self.margin = margin
        self.status = status

    def __dict__(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'symbol': self.symbol,
            'flag': self.flag,
            'side': self.side,
            'price': self.price,
            'volume': self.volume,
            'commission': self.commission,
            'margin': self.margin,
            'status': self.status
        }


class Trade(object):
    def __init__(self, datetime, order_id, symbol, flag, side, price, volume, profit):
        self.id = binascii.hexlify(os.urandom(12)).decode()
        self.datetime = datetime
        self.order_id = order_id
        self.symbol = symbol
        self.flag = flag
        self.side = side
        self.price = price
        self.volume = volume
        self.profit = profit

    def __dict__(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'flag': self.flag,
            'side': self.side,
            'price': self.price,
            'volume': self.volume,
            'profit': self.profit
        }


class Position(object):
    Long, Short = range(2)
    Directions = ['Long', 'Short']

    def __init__(self, symbol, cost, direction, volume, margin):
        self.symbol = symbol
        self.cost = cost
        self.direction = direction
        self.volume = volume
        self.margin = margin

    def __dict__(self):
        return {
            'symbol': self.symbol,
            'cost': self.cost,
            'direction': self.direction,
            'volume': self.volume,
            'margin': self.margin,
        }


class Profit(object):
    def __init__(self, datetime, amount):
        self.datetime = datetime
        self.amount = amount

    def __dict__(self):
        return {
            'datetime': self.datetime,
            'amount': self.amount
        }
