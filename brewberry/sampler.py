#
# Sampler.
#
# The object being logged should contain the following methods:
#  - read_time()
#  - read_temperature()
#  - read_heater()
#

from __future__ import absolute_import

from collections import namedtuple
from datetime import datetime
from .actors import spawn_link, ask, with_self_address
from .timer import timer


Sample = namedtuple('Sample', ['time', 'temperature', 'heater', 'controller', 'mash_temperature'])

SAMPLE_INTERVAL = 2

def _sample_as_dict(self):
    return {
        'time': self.time.isoformat()[:19],
        'temperature': self.temperature,
        'heater': self.heater,
        'controller': self.controller,
        'mash-temperature': self.mash_temperature
    }

Sample.as_dict = _sample_as_dict

@with_self_address
def Sampler(self, io, controller, receiver):

    spawn_link(timer, receiver=self, interval=SAMPLE_INTERVAL)

    def sample():
        receiver(Sample(datetime.utcfromtimestamp(io.read_time()),
                        io.read_temperature(),
                        io.read_heater(),
                        ask(controller, 'which_state'),
                        ask(controller, 'which_temperature')))
        return sample
    return sample()


# vim:sw=4:et:ai
