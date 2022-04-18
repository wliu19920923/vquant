import hmac
import time
import hashlib
from cacheout import LFUCache
from datetime import datetime
from urllib.parse import urlencode
from vquant.utils.request import Request

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
        response = self.http_requests(RequestMethod.GET, '/api/v3/account', params=self.sign())
        return {i['asset'].lower(): {
            'available': float(i['free']),
            'frozen': float(i['locked']),
            'total': float(i['free']) + float(i['locked']),
        } for i in response['balances']}

    def create_order(self, symbol, side, price, amount):
        response = self.http_requests(RequestMethod.POST, '/api/v3/order', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'side': side == 'bid' and 'BUY' or 'SELL',
            'price': self.num_decimal_string(price),
            'quantity': self.num_decimal_string(amount),
            'timeInForce': 'GTC',
            'type': 'LIMIT'
        }))
        return response.get('orderId')

    def cancel_order(self, symbol, order_id):
        response = self.http_requests(RequestMethod.DELETE, '/api/v3/order', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'orderId': int(order_id)
        }))
        return response.get('status') == Order.Canceled

    def order_detail(self, symbol, order_id):
        response = self.http_requests(RequestMethod.GET, '/api/v3/order', params=self.sign({
            'symbol': self.convert_symbol(symbol),
            'orderId': order_id
        }))
        return Order(str(response['orderId']), datetime.fromtimestamp(response['time'] / 1000), symbol, Order.Open, response['side'], float(response['price']), float(response['origQty']), response['status'], 0, Order.Created)

    def active_orders(self, symbol):
        response = self.http_requests(RequestMethod.GET, '/api/v3/openOrders', params=self.sign({
            'symbol': symbol
        }))
        return [Order(
            dt=datetime.fromtimestamp(order['time'] / 1000),
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
