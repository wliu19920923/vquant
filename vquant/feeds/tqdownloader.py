from datetime import datetime
from contextlib import closing
from tqsdk import TqApi, TqAuth
from tqsdk.tools import DataDownloader


class TianQinDownLoader(object):
    def __init__(self, username, password):
        self.api = TqApi(auth=TqAuth(username, password))
        self.download_tasks = dict()

    def create_download_task(self, exchange, symbol, minutes: int, start, end):
        interval = minutes * 60
        tq_symbol = '%s.%s' % (exchange, symbol)
        csv_file_name = '/tmp/%s.%s' % (tq_symbol, minutes)
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        self.download_tasks[tq_symbol] = DataDownloader(
            self.api, symbol_list=tq_symbol, dur_sec=interval,
            start_dt=start_date, end_dt=end_date, csv_file_name=csv_file_name
        )

    def start(self):
        with closing(self.api):
            while not all([v.is_finished() for v in self.download_tasks.values()]):
                self.api.wait_update()
                print('progress: ', {k: ('%.2f%%' % v.get_progress()) for k, v in self.download_tasks.items()})


if __name__ == '__main__':
    tqd = TianQinDownLoader('18512805580', 'ab123789')
