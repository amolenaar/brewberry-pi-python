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
from actors import ask

Sample = namedtuple('Sample', ['time', 'temperature', 'heater', 'controller', 'mash_temperature'])


def _sample_as_dict(self):
    return {
        'time': self.time.isoformat()[:19],
        'temperature': self.temperature,
        'heater': self.heater,
        'controller': self.controller,
        'mash-temperature': self.mash_temperature
    }

Sample.as_dict = _sample_as_dict


def Sampler(io, controller, receiver):
    print 'Sampler', io, controller, receiver
    receiver(Sample(datetime.utcfromtimestamp(io.read_time()),
                    io.read_temperature(),
                    io.read_heater(),
                    ask(controller, 'query_state'),
                    ask(controller, 'query_temperature')))
    return Sampler


# vim:sw=4:et:ai
