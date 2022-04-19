from datetime import datetime

StrTimeFormat = '%Y-%m-%d %H:%M:%S.%f'


def millisecond_to_str_time(ms):
    return datetime.fromtimestamp(int(ms) / 1000).strftime(StrTimeFormat)
