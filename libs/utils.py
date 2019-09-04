
from pyparsing import Word, alphas, Suppress, Combine, nums, string, Optional, Regex
from time import strftime
from datetime import datetime, time


def date_diff_in_seconds(date_start):
    date_start = date_start.split('.')[0]
    dt1 = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
    dt2 = datetime.now()

    timedelta = dt2 - dt1
    in_seconds = timedelta.days * 24 * 3600 + timedelta.seconds
    in_minutes = int(in_seconds / 60)
    return in_minutes


# thanks: https://gist.github.com/leandrosilva/3651640
class SyslogParser(object):
  def __init__(self):
    ints = Word(nums)

    # timestamp
    month = Word(string.ascii_uppercase, string.ascii_lowercase, exact=3)
    day   = ints
    hour  = Combine(ints + ":" + ints + ":" + ints)

    timestamp = month + day + hour

    # hostname
    hostname = Word(alphas + nums + "_" + "-" + ".")

    # appname
    appname = Word(alphas + "/" + "-" + "_" + ".") + Optional(Suppress("[") + ints + Suppress("]")) + Suppress(":")

    # message
    message = Regex(".*")

    # pattern build
    self.__pattern = timestamp + hostname + appname + message

  def parse(self, line):
    parsed = self.__pattern.parseString(line)

    payload              = {}
    payload["timestamp"] = strftime("%Y-%m-%d %H:%M:%S")
    payload["hostname"]  = parsed[3]
    payload["appname"]   = parsed[4]

    if len(parsed) > 6:
        payload["pid"]   = parsed[5]
        payload["message"]   = parsed[6]
    else:
        payload["message"]   = parsed[5]


    return payload