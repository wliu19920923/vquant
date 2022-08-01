import hashlib
import hmac
import json
import pandas
import time
import websocket
from datetime import datetime
from urllib.parse import urlencode
from vquant.utils.request import Request
from vquant.utils.timeutil import millisecond_to_str_time

BinanceSocketURL = 'wss://stream.binance.com:9443'


class BinanceSpotBroker(object):
    class Order:
        class Side:
            Buy, Sell = ('BUY', 'SELL')

        class Type:
            Market, Limit = ('MARKET', 'LIMIT')

        class Status:
            Created, Partial, Completed, Pending, Canceled, Expired, Rejected = ('NEW', 'PARTIALLY_FILLED', 'FILLED', 'PENDING_CANCEL', 'CANCELED', 'EXPIRED', 'REJECTED')

        Store = pandas.DataFrame(columns=['_id', 'datetime', 'symbol', 'direction', 'side', 'price', 'quantity', 'traded_quantity', 'commission', 'margin', 'status'])

        @staticmethod
        def create(_id, datetime, symbol, direction, side, price, quantity, traded_quantity, commission, margin, status):
            return pandas.Series(
                index=BinanceSpotBroker.Order.Store.frame.columns,
                data=[_id, datetime, symbol, direction, side, price, quantity, traded_quantity, commission, margin, status]
            )

        @staticmethod
        def submit(order):
            BinanceSpotBroker.Order.Store = BinanceSpotBroker.Order.Store.append(order, ignore_index=True)
            BinanceSpotBroker.Order.Store.set_index(BinanceSpotBroker.Order.Store['_id'])

    class Trade(object):
        Store = pandas.DataFrame(columns=['_id', 'datetime', 'order_id', 'direction', 'symbol', 'side', 'price', 'quantity'])

        @staticmethod
        def create(_id, datetime, order_id, symbol, side, price, quantity):
            return pandas.Series(
                index=BinanceSpotBroker.Order.Store.frame.columns,
                data=[_id, datetime, order_id, symbol, side, price, quantity]
            )

        @staticmethod
        def submit(trade):
            BinanceSpotBroker.Trade.Store = BinanceSpotBroker.Trade.Store.append(trade, ignore_index=True)
            BinanceSpotBroker.Trade.Store.set_index(BinanceSpotBroker.Trade.Store['_id'])

    class Position(object):
        class Direction:
            Long, Short = ('Long', 'Short')

        Store = pandas.DataFrame(columns=['_id', 'symbol', 'direction', 'quantity', 'margin', 'cost'])

        @staticmethod
        def create(symbol, direction, quantity, margin, cost):
            return pandas.Series(
                index=BinanceSpotBroker.Order.Store.frame.columns,
                data=[symbol + direction, symbol, direction, quantity, margin, cost]
            )

        @staticmethod
        def submit(position):
            BinanceSpotBroker.Position.Store = BinanceSpotBroker.Position.Store.append(position, ignore_index=True)
            BinanceSpotBroker.Position.Store.set_index(BinanceSpotBroker.Position.Store['_id'])

    QuoteAsset = 'USDT'
    ListenKeyDuration = 60 * 60

    def __init__(self, callback, **kwargs):
        self.callback = callback
        self.assets = dict()
        self.listen_key = self.get_listen_key()
        self.listen_key_expired_time = time.time() + self.ListenKeyDuration
        self.access_key = kwargs.get('access_key')
        self.secret_key = kwargs.get('secret_key')
        self.cash = 0
        self.value = 0
        self.available = 0
        self.frozen = 0
        self.profit = 0

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

    def http_requests(self, method, path, **kwargs):
        url = 'https://api3.binance.com' + path
        headers = {
            'X-MBX-APIKEY': self.access_key
        }
        return Request.http_requests(method, url, headers=headers, **kwargs)

    def balance(self):
        response = self.http_requests(Request.GET, '/api/v3/account', params=self.sign())
        return {i['asset'].lower(): {
            'available': float(i['free']),
            'frozen': float(i['locked']),
            'total': float(i['free']) + float(i['locked']),
        } for i in response['balances']}

    def create_order(self, symbol, side, price, quantity):
        params = dict(
            symbol=symbol, side=side, price=self.num_decimal_string(price), quantity=self.num_decimal_string(quantity),
            timeInForce='GTC', type=self.Order.Type.Limit
        )
        params = self.sign(params)
        response = self.http_requests(Request.POST, '/api/v3/order', params=params)
        return response.get('orderId')

    def cancel_order(self, symbol, order_id):
        params = dict(symbol=symbol, orderId=int(order_id))
        params = self.sign(params)
        response = self.http_requests(Request.DELETE, '/api/v3/order', params=params)
        return response.get('status') == self.Order.Status.Canceled

    def cancel_all_order(self, symbol):
        response = self.http_requests(Request.DELETE, '/api/v3/openOrders', params=self.sign({
            'symbol': self.convert_symbol(symbol)
        }))
        for order in response:
            orders = self.Order.Store.loc[self.Order.Store['_id'] == str(order['orderId'])]
            self.Order.Store.loc[orders.index, ['status']] = order['status']
            self.callback('on_order', dict(_id=str(order['orderId']), status=order['status']))

    def order_detail(self, symbol, order_id):
        params = dict(symbol=self.convert_symbol(symbol), orderId=order_id)
        params = self.sign(params)
        response = self.http_requests(Request.GET, '/api/v3/order', params=params)
        return Order(str(response['orderId']), datetime.fromtimestamp(response['time'] / 1000), symbol, Order.Open, response['side'], float(response['price']), float(response['origQty']),
                     response['status'], 0, Order.Created)

    def active_orders(self, symbol):
        params = dict(symbol=self.convert_symbol(symbol))
        response = self.http_requests(Request.GET, '/api/v3/openOrders', params=params)
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
        params = dict(symbol=self.convert_symbol(symbol), limit=1000)
        params = self.sign(params)
        response = self.http_requests(Request.GET, '/api/v3/myTrades', params=params)
        return [Trade(
            dt=millisecond_to_str_time(trade['time']),
            trade_id=trade['id'],
            order_id=trade['orderId'],
            symbol=symbol,
            flag=Order.Open,
            side=Order.Buy if trade['isBuyer'] else Order.Sell,
            price=self.num_decimal_string(trade['price']),
            volume=self.num_decimal_string(trade['qty']),
            profit=0,
        ) for trade in response]

    def get_listen_key(self):
        response = self.http_requests(Request.POST, '/api/v3/userDataStream')
        return response.get('listenKey')

    def extend_listen_key_time(self):
        now = time.time()
        if self.listen_key_expired_time - now >= 60:
            return
        params = dict(listenKey=self.listen_key)
        self.http_requests(Request.PUT, '/api/v3/userDataStream', params=params)
        self.listen_key_expired_time = now + self.ListenKeyDuration

    def on_value(self, value):
        self.store.insert_value(value)

    def on_asset(self, value):
        self.cash = value

    def on_order(self, order: Order):
        self.store.update_or_insert_order(order.__dict__())
        self.cerebro.notify_order(order)

    def on_position(self, position: Position):
        self.store.update_or_insert_position(position.__dict__())

    def balanceUpdate(self, data):
        # dt, oid, symbol, flag, side, price, volume, commission, margin, status
        if data['a'] == self.QuoteAsset:
            self.on_asset(float(data['d']))

    def executionReport(self, data):
        order = Order(millisecond_to_str_time(data['O']), data['i'], data['s'], Order.Open, data['S'], float(data['p']), float(data['q']), float(data['n']), 0, data['X'])
        self.on_order(order)

    def outboundAccountPosition(self, data):
        pass

    def on_open(self, ws):
        pass

    def on_message(self, ws, message):
        try:
            stream = json.loads(message)
            if 'ping' in stream:
                ws.send(json.dumps({
                    'pong': stream['ping']
                }))
            else:
                event = stream.get('e')
                function = getattr(self, event)
                function(stream)
        except Exception as exp:
            print(exp)
        self.extend_listen_key_time()

    def on_error(self, _, error):
        error_exp = type(error)
        if error_exp in (ConnectionRefusedError, websocket.WebSocketConnectionClosedException):
            self.start()
        raise error_exp

    def on_close(self, _, close_status_code, close_msg):
        raise ConnectionError(close_status_code, close_msg)

    def start(self):
        url ='wss://stream.binance.com:9443/stream?streams=' + self.listen_key
        ws = websocket.create_connection(
            url=url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.run_forever()
