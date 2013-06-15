#
# Sampler.
#
# The object being logged should contain the following methods:
#  - read_time()
#  - read_temperature()
#  - read_heater()
#

from collections import namedtuple

Sample = namedtuple('Sample', ['time', 'temperature', 'heater'])

def _sample_as_dict(self):
    return {
        'time': self.time.isoformat(),
        'temperature': self.temperature,
        'heater': self.heater
    }

Sample.as_dict = _sample_as_dict

def sample(io):
    return Sample(io.read_time(), io.read_temperature(), io.read_heater())


class Sampler(object):
    def __init__(self, io):
        self._io = io
        self.observers = set()

    def notify(self, sample):
        print self.observers
        for observer in list(self.observers):
            observer(sample)

    def __call__(self):
        s = sample(self._io)
        self.notify(s)
        return s

# vim:sw=4:et:ai
