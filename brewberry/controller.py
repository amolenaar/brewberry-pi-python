"""
Control the system.
"""

# Energy requires to raise the temperature of 1 litre of water by 1 degrees (C)
JOULES_1_LITRE = 4186


class Config(object):

    def __init__(self, power = 2000, efficiency = .5, litres = 17):
        self.power = power
        self.efficiency = efficiency
        self.litres = litres

    def time(self, dtemp):
        return (JOULES_1_LITRE * self.litres) / (self.power * self.efficiency)


class Controller(object):
    config = Config()

    def __init__(self, io):
        self._io = io
        self.mash_temperature = 0
        self._started = Off

    def _set_started(self, v):
        self._started = v and On or Off
        self()

    started = property(lambda s: s._started, _set_started)

    def __call__(self):
        io = self._io
        if self._started and self.mash_temperature > io.read_temperature():
            if not io.read_heater():
                io.set_heater(True)
        else:
            if io.read_heater():
                io.set_heater(False)

# vim:sw=4:et:ai
