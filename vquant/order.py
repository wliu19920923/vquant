import os
import binascii
from matcher import Matcher


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

    Market, Limit = range(2)
    Types = ['Market', 'Limit']

    Created, Submitted, Accepted, Partial, Completed, Canceled, Expired, Margin, Rejected = range(9)
    Status = [
        'Created', 'Submitted', 'Accepted', 'Partial', 'Completed',
        'Canceled', 'Expired', 'Margin', 'Rejected',
    ]

    def __init__(self, broker):
        self.broker = broker

    @property
    def order_id(self):
        return binascii.hexlify(os.urandom(12)).decode()

    def check_order_cash_use(self, order):
        cash_use = order['commission'] + order['margin']
        return self.broker.available > cash_use

    def deduction_deposit(self, order):
        self.broker.commission_frozen += order['commission']
        self.broker.margin_use += order['margin']
        self.broker.available = self.broker.available - order['commission'] - order['margin']
        order['status'] = Order.Accepted
        return order

    def submit(self, order):
        order['status'] = Order.Submitted
        self.broker.on_order(order)
        if not self.check_order_cash_use(order):
            order['status'] = Order.Margin
            self.broker.on_order(order)
            return
        order = self.deduction_deposit(order)
        self.broker.on_order(order)
        return Matcher(self, order).exec()

    def create(self, flag, side, type, price, volume):
        cost = price * volume
        margin = cost * self.broker.margin_rate
        commission = volume * self.broker.commission
        order = dict(
            order_id=self.order_id, create_time=self.broker.cerebro.timestamp, update_time=self.broker.cerebro.timestamp,
            flag=flag, side=side, type=type, price=price, volume=volume,
            commission=commission, marigin=margin, status=Order.Created
        )
        self.broker.on_order(order)
        return self.submit(order)

    def cancel(self, order):
        order['update_time'] = self.broker.cerebro.timestamp
        order['status'] = self.Canceled
        self.broker.on_order(order)
