"""
Control the system.
"""

from actors import spawn

# Energy requires to raise the temperature of 1 litre of water by 1 degrees (C)
JOULES_1_LITRE = 4186


class Config(object):

    def __init__(self, power = 2000, efficiency = .80, volume = 17):
        self.power = power # Watts
        self.efficiency = efficiency
        self.volume = volume # litres
        self.wait_time = 20 # seconds

    def time(self, dtemp):
        return max((dtemp * JOULES_1_LITRE * self.volume) / (self.power * self.efficiency), self.wait_time)


class Controller(object):
    config = Config()

    def __init__(self, io):
        self._io = io
        self._temperature = 0
        self._act = spawn(idle_state_machine, self._io)

    def update_state_machine(self, new_act, *args, **kwargs):
        if self._act:
            self._act(stop=True)
        self._act = spawn(new_act, *args, **kwargs)

    def __call__(self, tick=None, start=None, temperature=None, query_temperature=None, query_state=None):
        """
        Handle incoming messages.
        """
        if temperature is not None:
            self._temperature = temperature
            self.update_state_machine(state_machine, self._io, self.config, temperature)
        elif start is not None:
            if start:
                self.update_state_machine(state_machine, self._io, self.config, self._temperature)
            else:
                self.update_state_machine(idle_state_machine, self._io)
        elif query_temperature:
            query_temperature(self._temperature)
        elif query_state:
            self._act(query_state=query_state)
        elif tick:
            self._act()
        return self.__call__


def state(func):
    def state_decorator(stop=None, query_state=None):
        if stop:
            return
        elif query_state:
            query_state(func.__name__)
            return state_decorator
        else:
            return func()
    return state_decorator


def idle_state_machine(io):

    @state
    def Idle():
        """
        Initial (start) state. System is Idle. Heater is turned off if required.
        """
        if io.read_heater():
            io.set_heater(Off)
        return Idle
    return Idle()


def state_machine(io, config, mash_temperature):

    @state
    def Heating():
        """
        . calculate time to heat
        . Heat as long as the timer has not elapsed
        . Heating is done for at least 30 seconds.
        """
        dT = mash_temperature - io.read_temperature()

        if dT <= 0:
            return Resting

        end_time = io.read_time() + config.time(dT)

        io.set_heater(On)

        @state
        def Heating():
            t = io.read_time()
            if t >= end_time:
                return Slacking
            return Heating
        return Heating

    @state
    def Slacking():
        """
        . Keep track of x last temperatures
        . Define dtemp over x temperature readings
        . If dtemp < y go to next stage
        . Stay in this state for at least 30 seconds.
        """
        io.set_heater(Off)

        end_time = io.read_time() + config.wait_time
        sliding_window = []

        @state
        def Slacking():
            t = io.read_time()
            sliding_window.append(io.read_temperature())
            if t > end_time and \
                            len(sliding_window) > 10 and \
                            abs(sliding_window[-10] - sliding_window[-1]) < 0.05:
                return Resting
            return Slacking
        return Slacking

    @state
    def Resting():
        """
        . keep track of last temperature reading
        . If t_mash < y-d degrees, go to next stage
        """
        if io.read_heater():
            io.set_heater(Off)

        if mash_temperature - io.read_temperature() > 0.1:
            return Heating
        return Resting

    return Resting()


# vim:sw=4:et:ai
