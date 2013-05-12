#
# Logger.
#
# The object being logged should contain the following methods:
#  - read_time()
#  - read_temperature()
#  - read_heater()
#

from collections import namedtuple
import datetime

TEMPERATURE_DELTA = 0.05
TIME_DELTA = datetime.timedelta(seconds=60)

LogLine = namedtuple('LogLine', ['time', 'temperature', 'heater'])

def log(io):
    return LogLine(io.read_time(), io.read_temperature(), io.read_heater())

def different(log_line, last_log_line):
    return not last_log_line or \
           log_line.time >= last_log_line.time + TIME_DELTA or \
           abs(log_line.temperature - last_log_line.temperature) >= TEMPERATURE_DELTA or \
           log_line.heater != last_log_line.heater

class Logger(object):
    def __init__(self, io, appender):
        self._io = io
        self.last = None
        self._appender = appender

    def __call__(self):
        log_line = log(self._io)
        if different(log_line, self.last):
            self._appender(log_line)
        self.last = log_line
        return log_line

import json

def json_appender(file):
    def jsonifier(log_line):
        json.dump({
            'time': log_line.time.isoformat(),
            'temperature': log_line.temperature,
            'heater': log_line.heater
        }, file)
        file.write('\n')
    return jsonifier

# vim:sw=4:et:ai
