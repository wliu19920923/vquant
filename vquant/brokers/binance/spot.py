import hmac
import time
import hashlib
import requests
from cacheout import LFUCache
from datetime import datetime
from urllib.parse import urlencode


class BinanceSpotBroker(object):
    class Order(object):
        Open = 'Open'
        Flags = {Open: 'Open'}

        Buy, Sell = ('BUY', 'SELL')
        Sides = {'BUY': 'Buy', 'SELL': 'Sell'}

        Created, Partial, Completed, Pending, Canceled, Expired, Rejected = ('NEW', 'PARTIALLY_FILLED', 'FILLED', 'PENDING_CANCEL', 'CANCELED', 'EXPIRED', 'REJECTED')
        Status = {'NEW': 'Created', 'PARTIALLY_FILLED': 'Partial', 'FILLED': 'Completed', 'PENDING_CANCEL': 'Pending', 'CANCELED': 'Canceled', 'EXPIRED': 'Expired', 'REJECTED': 'Rejected'}

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

    def __init__(self, access_key, secret_key):
        self.cache = LFUCache()
        self.base_url = 'https://api3.binance.com'
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

    def http_requests(self, method, path, params=None):
        """
        统一请求类
        :param method: 方法
        :param path: 路径
        :param params: 参数
        :return: 获取的json结果
        """
        url = self.base_url + path
        params = params or dict()
        response = requests.request(method, url, params=params, headers=self.http_headers)
        try:
            result = response.json()
        except Exception as exp:
            raise TypeError(response.text)
        else:
            return result

    def sign(self, params=None):
        params = params and params or dict()
        params['timestamp'] = int(time.time() * 1000)
        params['recvWindow'] = 5000
        params['signature'] = hmac.new(self.secret_key.encode(), urlencode(params).encode(), digestmod=hashlib.sha256).hexdigest()
        return params

    def balance(self):
        response = self.http_requests('GET', '/api/v3/account', self.sign())
        return {i['asset'].lower(): {
            'available': float(i['free']),
            'frozen': float(i['locked']),
            'total': float(i['free']) + float(i['locked']),
        } for i in response['balances']}

    def create_order(self, symbol, side, price, amount):
        response = self.http_requests('POST', '/api/v3/order', self.sign({
            'symbol': self.convert_symbol(symbol),
            'side': side == 'bid' and 'BUY' or 'SELL',
            'price': self.num_decimal_string(price),
            'quantity': self.num_decimal_string(amount),
            'timeInForce': 'GTC',
            'type': 'LIMIT'
        }))
        return response.get('orderId')

    def cancel_order(self, symbol, order_id):
        response = self.http_requests('DELETE', '/api/v3/order', self.sign({
            'symbol': self.convert_symbol(symbol),
            'orderId': int(order_id)
        }))
        return response.get('status') == 'CANCELED'

    def order_detail(self, symbol, order_id):
        response = self.http_requests('GET', '/api/v3/order', self.sign({
            'symbol': self.convert_symbol(symbol),
            'orderId': order_id
        }))
        return self.Order(str(response['orderId']), datetime.fromtimestamp(response['time'] / 1000), symbol, self.Order.Open, response['side'], float(response['price']), float(response['origQty']), response['status'])

    def active_orders(self, symbol, page=1, limit=100):
        response = self.http_requests('GET', '/api/v3/openOrders', self.sign({
            'symbol': symbol
        }))
        return [self.order_format(symbol, order) for order in response]
