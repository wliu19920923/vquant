from datetime import datetime, date
from contextlib import closing
from tqsdk import TqApi, TqAuth, TqSim
from tqsdk.tools import DataDownloader

api = TqApi(auth=TqAuth("15989454209", "Xperiaqq1mp2"))
download_tasks = {}
# 下载从 2018-01-01 到 2018-09-01 的 SR901 日线数据
download_tasks["J_min30"] = DataDownloader(api, symbol_list="DCE.j2201", dur_sec=30*60,
                    start_dt=date(2018, 1, 1), end_dt=date(2022, 1, 17), csv_file_name="j2201_min30.csv")

with closing(api):
    while not all([v.is_finished() for v in download_tasks.values()]):
        api.wait_update()
        print("progress: ", { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() })
