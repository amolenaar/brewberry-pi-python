"""
Control the system.
"""

# Energy requires to raise the temperature of 1 litre of water by 1 degrees (C)
JOULES_1_LITRE = 4186


class Config(object):

    def __init__(self, power = 2000, efficiency = .75, volume = 17):
        self.power = power # Watts
        self.efficiency = efficiency
        self.volume = volume # litres
        self.slack = 120 # seconds

    def time(self, dtemp):
        return (JOULES_1_LITRE * self.volume) / (self.power * self.efficiency)


class Controller(object):
    config = Config()

    def __init__(self, io):
        self._io = io
        self.mash_temperature = 0
        self._started = Off
        self.act = self.Resting

    def state(self):
        if self._started:
            return self.act.__name__

    def _set_started(self, v):
        self._started = v and On or Off
        self()

    started = property(lambda s: s._started, _set_started)

    def __call__(self):
        io = self._io
        if self._started:
            new_state = self.act()
            if new_state: self.act = new_state
        else:
            io.set_heater(Off)

    def Heating(self):
        """
        . calculate time to heat
        . Heat as long as the timer has not elapsed
        """
        io = self._io
        temp = io.read_temperature()
        dT = (self.mash_temperature - temp)

        if dT < 0:
            return self.Resting

        watts = (self.config.power * self.config.efficiency)
        start_time = io.read_time()
        # Heat for at least 30 seconds
        end_time = start_time + max(self.config.volume * dT * 4186 / watts, 30)

        io.set_heater(On)

        def Heating():
            t = io.read_time()
            if t >= end_time:
                io.set_heater(Off)
                return self.Slacking
        return Heating

    def Slacking(self):
        """
        . Keep track of x last temperatures
        . Define dtemp over x temperature readings
        . If dtemp < y go to next stage
        """
        io = self._io
        end_time = io.read_time() + 30
        self.sliding_window = []
        def Slacking():
            t = io.read_time()
            s = self.sliding_window
            s.append(io.read_temperature())
            if t > end_time and len(s) > 10 and abs(s[-10] - s[-1]) < 0.05:
                return self.Resting
        return Slacking


    def Resting(self):
        """
        . keep track of last temperature reading
        . If t_mash < y-d degrees, go to next stage
        """
        io = self._io
        if self.mash_temperature - io.read_temperature() > 0.1:
            return self.Heating


# vim:sw=4:et:ai
