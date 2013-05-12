#
# Logger.
#
# The object being logged should contain the following methods:
#  - read_time()
#  - read_temperature()
#  - read_heater()
#

from collections import namedtuple

LogLine = namedtuple('LogLine', ['time', 'temperature', 'heater'])

def log(io):
    return LogLine(io.read_time(), io.read_temperature(), io.read_heater())

def different(log_line, last_log_line):
    return abs(log_line.temperature - last_log_line.temperature) > 0.01 or \
           log_line.heater != last_log_line.heater

class Logger(object):
    def __init__(self, io):
        self._io = io
        self.lines = []

    def __call__(self):
        log_line = log(self._io)
        try:
            last = self.lines[-1]
            if different(log_line, last):
                self.lines.append(log_line)
        except IndexError:
            self.lines.append(log_line)
        return log_line

# vim:sw=4:et:ai
