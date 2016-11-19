#
# Logger.
#

import datetime

TEMPERATURE_DELTA = 0.07 # degrees Celcius
TIME_DELTA = datetime.timedelta(seconds=60)


def different(sample, prev_sample):
    return not prev_sample or \
           sample.time >= prev_sample.time + TIME_DELTA or \
           abs(sample.temperature - prev_sample.temperature) >= TEMPERATURE_DELTA or \
           sample.heater != prev_sample.heater or \
           sample.controller != prev_sample.controller

class Logger(object):
    def __init__(self, appender):
        self.prev_sample = None
        self._appender = appender

    def __call__(self, sample):
        if different(sample, self.prev_sample):
            self._appender(sample)
            self.prev_sample = sample
        return self.__call__

import json

def json_appender(filename):
    def jsonifier(sample):
        with open(filename, 'w') as file:
            json.dump(sample.as_dict(), file)
            file.write('\n')
            file.flush()
    return jsonifier


def SessionLogger(log_file):
    return Logger(json_appender(log_file))


# vim:sw=4:et:ai
