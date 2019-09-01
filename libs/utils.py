
from datetime import datetime, time


def date_diff_in_seconds(date_start): 
    date_start = date_start.split('.')[0]
    dt1 = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
    dt2 = datetime.now()

    timedelta = dt2 - dt1
    in_seconds = timedelta.days * 24 * 3600 + timedelta.seconds
    in_minutes = int(in_seconds / 60)
    return in_minutes