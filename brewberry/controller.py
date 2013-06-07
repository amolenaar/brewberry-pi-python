"""
Control the system.
"""

class Controller(object):

    def __init__(self, io):
        self._io = io
        self.mash_temperature = None

    def __call__(self):
        io = self._io
        if self.mash_temperature > io.read_temperature():
            if not io.read_heater():
                io.set_heater(True)
        else:
            if io.read_heater():
                io.set_heater(False)

# vim:sw=4:et:ai
