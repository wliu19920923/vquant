import json
import pandas
import websocket
from datetime import datetime

BaseDuration = 60000000000


class TianQinOpenFeed(object):
    ws_url = 'wss://openmd.shinnytech.com/t/md/front/mobile'
    fields = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    duration = 60000000000

    def __init__(self, exchange, symbol, callback):
        self.ins = '%s.%s' % (exchange.upper(), symbol)
        self.data = pandas.DataFrame(columns=self.fields)
        self.callback = callback

    def update_or_insert_kline(self, kline, is_last):
        values = [
            datetime.fromtimestamp(kline['datetime'] / 1000 ** 3).strftime('%Y-%m-%d %H:%M:%S'),
            kline['open'], kline['high'], kline['low'], kline['close'], kline['volume']
        ]
        records = self.data.loc[self.data['datetime'] == values[0]]
        if len(records.index):
            self.data.loc[records.index, self.fields] = values
        else:
            record = {self.fields[i]: values[i] for i in range(6)}
            self.data = self.data.append([record], ignore_index=True)
        if is_last:
            self.callback(values[0])

    def analytical_kline(self, tick):
        try:
            print(tick)
            klines = tick['data'][0]['klines'][self.ins][str(self.duration)]['data']
            is_last = len(klines) == 1
            for kline in klines.values():
                self.update_or_insert_kline(kline, is_last)
        except Exception as exp:
            print(exp)

    @staticmethod
    def on_pong(ws):
        ws.send(json.dumps({
            'aid': 'peek_message'
        }))

    def on_open(self, ws):
        ws.send(json.dumps({
            'aid': 'set_chart',
            'chart_id': 'PC_kline_chart',
            'ins_list': self.ins,
            'duration': self.duration,
            'view_width': 2000
        }))

    def on_message(self, ws, message):
        tick = json.loads(message)
        self.analytical_kline(tick)
        self.on_pong(ws)

    def on_error(self, _, error):
        error_exp = type(error)
        if error_exp in (ConnectionRefusedError, websocket.WebSocketConnectionClosedException):
            self.connect()
        raise error_exp

    def on_close(self, _, close_status_code, close_msg):
        raise ConnectionError(close_status_code, close_msg)

    def connect(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.run_forever()


if __name__ == '__main__':
    def msg(msg):
        print(msg)
        print(tf.data)


    tf = TianQinOpenFeed('CFFEX', 'IF2206', msg)
    tf.connect()
