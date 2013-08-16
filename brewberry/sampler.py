#
# Sampler.
#
# The object being logged should contain the following methods:
#  - read_time()
#  - read_temperature()
#  - read_heater()
#

from collections import namedtuple
from datetime import datetime

Sample = namedtuple('Sample', ['time', 'temperature', 'heater', 'controller', 'mash_temperature'])

def _sample_as_dict(self):
    return {
        'time': self.time.isoformat(),
        'temperature': self.temperature,
        'heater': self.heater,
        'controller': self.controller,
        'mash-temperature': self.mash_temperature
    }

Sample.as_dict = _sample_as_dict

def sample(io, controller):
    return Sample(datetime.utcfromtimestamp(io.read_time()), io.read_temperature(), io.read_heater(),
                  controller.state(), controller.mash_temperature)


class Sampler(object):
    def __init__(self, io, controller):
        self._io = io
        self._controller = controller
        self.observers = set()

    def notify(self, sample):
        #print self.observers
        for observer in list(self.observers):
            observer(sample)

    def __call__(self):
        s = sample(self._io, self._controller)
        self.notify(s)
        return s

# vim:sw=4:et:ai
