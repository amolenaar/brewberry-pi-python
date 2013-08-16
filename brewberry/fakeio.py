
# Fake (test/reference, whatever you like) implementation for IO.
# It's a module: there's only one for the entire system.
import datetime
import math

INTERVAL = 1000 # ms

time = 0
static_time = True
temperature = 0
heater = Off

def read_time():
    global time
    try:
        return time
    finally:
        if not static_time:
            time += INTERVAL / 1000.

def read_temperature():
    return temperature + math.sin(time / 20.0)

def read_heater():
    return heater

def set_heater(val):
    global heater
    heater = val
    return heater

# vim:sw=4:et:ai
