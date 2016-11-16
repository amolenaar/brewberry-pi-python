
# Fake (test/reference, whatever you like) implementation for IO.
# It's a module: there's only one for the entire system.
import math

time = 0
temperature = 0
heater = Off

time_updater = lambda t: t

def read_time():
    global time
    try:
        return time
    finally:
        time = time_updater(time)

def read_temperature():
    return temperature + math.sin(time / 20.0)

def read_heater():
    return heater

def set_heater(val):
    global heater
    heater = val
    return heater

# vim:sw=4:et:ai
