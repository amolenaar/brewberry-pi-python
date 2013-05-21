
# Fake (test/reference, whatever you like) implementation for IO.
# It's a module: there's only one for the entire system.
import datetime
import math

time = 0
temperature = 0
heater = Off

def read_time():
    global time
    try:
        return datetime.datetime.utcfromtimestamp(time)
    finally:
        time += 1

def read_temperature():
    return temperature + math.sin(time / 20)

def read_heater():
    return heater


# vim:sw=4:et:ai
