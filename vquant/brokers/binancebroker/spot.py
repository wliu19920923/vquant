import hmac
import time
import hashlib
from cacheout import LFUCache
from datetime import datetime
from urllib.parse import urlencode
from vquant.utils.request import Request
from vquant.utils.timeutil import millisecond_to_str_time

BinanceBaseURL = 'https://api3.binance.com'


class Order(object):
    Open = 'Open'
    Flags = {Open: 'Open'}

    Buy, Sell = ('BUY', 'SELL')
    Sides = {Buy: 'Buy', Sell: 'Sell'}

    Created, Partial, Completed, Pending, Canceled, Expired, Rejected = ('NEW', 'PARTIALLY_FILLED', 'FILLED', 'PENDING_CANCEL', 'CANCELED', 'EXPIRED', 'REJECTED')
    Status = {Created: 'Created', Partial: 'Partial', Completed: 'Completed', Pending: 'Pending', Canceled: 'Canceled', Expired: 'Expired', Rejected: 'Rejected'}

    def __init__(self, dt, oid, symbol, flag, side, price, volume, commission, margin, status):
        self.id = oid
        self.datetime = dt
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
    def __init__(self, dt, trade_id, order_id, symbol, flag, side, price, volume, profit):
        self.id = trade_id
        self.datetime = dt
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
    def __init__(self, symbol, cost, volume):
        self.symbol = symbol
        self.cost = cost
        self.volume = volume

    def __dict__(self):
        return {
            'symbol': self.symbol,
            'cost': self.cost,
            'volume': self.volume,
        }


class WebsocketStream(object):
    def __init__(self, access_key):
        self.listen_key = None
        self.listen_key_expired_time = time.time()
        self.http_headers = {
            'X-MBX-APIKEY': access_key
        }

    def extend_listen_key_time(self):
        params = dict(listenKey=self.listen_key)
        Request.http_requests(Request.PUT, BinanceBaseURL + '/api/v3/userDataStream', params=params, headers=self.http_headers)

    def get_listen_key(self):
        now = time.time()
        if not self.listen_key:
            response = Request.http_requests(Request.POST, BinanceBaseURL + '/api/v3/userDataStream', headers=self.http_headers)
            self.listen_key = response.get('listenKey')
            self.listen_key_expired_time = now + 60 * 60
        if self.listen_key_expired_time - now <= 60:
            self.extend_listen_key_time()
        return self.listen_key

    def on_open(self, ws):
        pass

    def on_message(self, ws, message):
        pass

    def start(self):
        pass


class BinanceSpotBroker(object):
    def __init__(self, access_key, secret_key):
        self.cache = LFUCache()
        self.secret_key = secret_key
        self.http_headers = {
            'X-MBX-APIKEY': access_key
        }

    @staticmethod
    def convert_symbol(symbol):
        return symbol.replace('_', '').upper()

    @staticmethod
    def num_decimal_places(value):
        return '.' in value and len(value.strip('0').strip('.')) or 0

    @staticmethod
    def num_decimal_string(value):
        return ('%f' % value).rstrip('0')

    def sign(self, params=None):
        params = params and params or dict()
        params['timestamp'] = int(time.time() * 1000)
        params['recvWindow'] = 5000
        params['signature'] = hmac.new(self.secret_key.encode(), urlencode(params).encode(), digestmod=hashlib.sha256).hexdigest()
        return params

    def balance(self):
        response = Request.http_requests(Request.GET, BinanceBaseURL + '/api/v3/account', params=self.sign())
        return {i['asset'].lower(): {
            'available': float(i['free']),
            'frozen': float(i['locked']),
            'total': float(i['free']) + float(i['locked']),
        } for i in response['balances']}

    def create_order(self, symbol, side, price, amount):
        response = Request.http_requests(Request.POST, BinanceBaseURL + '/api/v3/order', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'side': side == 'bid' and 'BUY' or 'SELL',
            'price': self.num_decimal_string(price),
            'quantity': self.num_decimal_string(amount),
            'timeInForce': 'GTC',
            'type': 'LIMIT'
        }))
        return response.get('orderId')

    def cancel_order(self, symbol, order_id):
        response = Request.http_requests(Request.DELETE, BinanceBaseURL + '/api/v3/order', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'orderId': int(order_id)
        }))
        return response.get('status') == Order.Canceled

    def cancel_all_order(self, symbol):
        response = Request.http_requests(Request.DELETE, BinanceBaseURL + '/api/v3/openOrders', params=self.sign({
            'symbol': self.convert_symbol(symbol)
        }))
        return [Order(
            dt=datetime.fromtimestamp(order['time'] / 1000),
            oid=str(order['orderId']),
            flag=Order.Open,
            symbol=symbol,
            side=Order.Buy if order['side'] == 'BUY' else Order.Sell,
            price=float(order['price']),
            volume=float(order['origQty']),
            commission=0,
            margin=0,
            status=order['status']
        ) for order in response]

    def order_detail(self, symbol, order_id):
        response = Request.http_requests(Request.GET, BinanceBaseURL + '/api/v3/order', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'orderId': order_id
        }))
        return Order(str(response['orderId']), datetime.fromtimestamp(response['time'] / 1000), symbol, Order.Open, response['side'], float(response['price']), float(response['origQty']), response['status'], 0, Order.Created)

    def active_orders(self, symbol):
        response = Request.http_requests(Request.GET, BinanceBaseURL + '/api/v3/openOrders', params=self.sign({
            'symbol': symbol
        }))
        return [Order(
            dt=millisecond_to_str_time(order['time']),
            oid=order['orderId'],
            flag=Order.Open,
            symbol=symbol,
            side=Order.Buy if order['side'] == 'BUY' else Order.Sell,
            price=float(order['price']),
            volume=float(order['origQty']),
            commission=0,
            margin=0,
            status=order['status']
        ) for order in response]

    def history_trades(self, symbol):
        response = await Request.http_requests(Request.GET, '/api/v3/myTrades', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'limit': 1000
        }))
        return [Trade(
            dt=millisecond_to_str_time(trade['time']),
            trade_id=trade['id'],
            order_id=trade['orderId'],
            symbol=symbol,
            flag=Order.Open,
            side=Order.Buy if trade['isBuyer'] else Order.Sell,
            price=self.num_decimal_string(trade['price']),
            volume=self.num_decimal_string(trade['qty'])
        ) for trade in response]
