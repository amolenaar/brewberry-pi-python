"""
Control the system.
"""

from __future__ import absolute_import

from .actors import spawn_link, with_self_address, kill
from .timer import timer

# Energy requires to raise the temperature of 1 litre of water by 1 degrees (C)
JOULES_1_LITRE = 4186
SAMPLE_INTERVAL = 2


class Config(object):

    def __init__(self, power = 2000, efficiency = .80, volume = 17):
        self.power = power # Watts
        self.efficiency = efficiency
        self.volume = volume # litres
        self.wait_time = 20 # seconds

    def time(self, dtemp):
        return max((dtemp * JOULES_1_LITRE * self.volume) / (self.power * self.efficiency), self.wait_time)


def Controller(io, config=Config(), set_temperature=0, state_machine=None):

    def controller(tick=None, start=None, temperature=None, which_temperature=None, which_state=None):
        if temperature is not None:
            return Controller(io, config, temperature, state_machine)(start=bool(state_machine))
        elif start is not None:
            if state_machine:
                state_machine(stop=True)

            new_fsm = spawn_link(mash_state_machine, io, config, set_temperature) if start else None
            return Controller(io, config, set_temperature, new_fsm)
        elif which_temperature:
            which_temperature(set_temperature)
        elif which_state:
            state_machine(which_state=which_state) if state_machine else which_state('Idle')
        elif tick:
            state_machine()
        return controller

    return controller


@with_self_address
def mash_state_machine(self, io, config, mash_temperature):

    my_timer = spawn_link(timer, receiver=self, interval=SAMPLE_INTERVAL)

    def state(func):
        def state_decorator(stop=None, which_state=None):
            if stop:
                kill(my_timer)
                if io.read_heater():
                    io.set_heater(Off)
                return
            elif which_state:
                which_state(func.__name__)
                return state_decorator
            else:
                return func()
        state_decorator.__name__ = func.__name__
        return state_decorator

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
