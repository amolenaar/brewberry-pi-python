"""
Control the system.
"""

class Controller(object):

    def __init__(self, io):
        self._io = io
        self.mash_temperature = 0
        self._started = Off

    def _set_started(self, v):
        self._started = v and On or Off

    started = property(lambda s: s._started, _set_started)

    def __call__(self):
        if not self._started: return
        io = self._io
        if self.mash_temperature > io.read_temperature():
            if not io.read_heater():
                io.set_heater(True)
        else:
            if io.read_heater():
                io.set_heater(False)

# vim:sw=4:et:ai
