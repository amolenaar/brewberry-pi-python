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
        self.wait_time = 30 # seconds

    def time(self, dtemp):
        return max((JOULES_1_LITRE * self.volume) / (self.power * self.efficiency), self.wait_time)


class Controller(object):
    config = Config()

    def __init__(self, io):
        self._io = io
        self.mash_temperature = 0
        self.act = self.Idle

    def __str__(self):
        return self.act.__name__

    def _set_started(self, v):
        self.act = v and self.Resting or self.Idle
        self()

    started = property(lambda s: s.act != s.Idle, _set_started)

    def __call__(self):
        new_state = self.act()
        if new_state: self.act = new_state

    ## The state machine:

    def Idle(self):
        """
        Initial (start) state. System is Idle. Heater is turned off if required.
        """
        io = self._io
        if io.read_heater():
            io.set_heater(Off)

    def Heating(self):
        """
        . calculate time to heat
        . Heat as long as the timer has not elapsed
        . Heating is done for at least 30 seconds.
        """
        io = self._io
        dT = self.mash_temperature - io.read_temperature()

        if dT <= 0:
            return self.Resting

        end_time = io.read_time() + self.config.time(dT)

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
        . Stay in this state for at least 30 seconds.
        """
        io = self._io
        if io.read_heater():
            io.set_heater(Off)

        end_time = io.read_time() + self.config.wait_time
        sliding_window = []
        def Slacking():
            t = io.read_time()
            sliding_window.append(io.read_temperature())
            if t > end_time and \
                            len(sliding_window) > 10 and \
                            abs(sliding_window[-10] - sliding_window[-1]) < 0.05:
                return self.Resting
        return Slacking


    def Resting(self):
        """
        . keep track of last temperature reading
        . If t_mash < y-d degrees, go to next stage
        """
        io = self._io
        if io.read_heater():
            io.set_heater(Off)

        if self.mash_temperature - io.read_temperature() > 0.1:
            return self.Heating


# vim:sw=4:et:ai
