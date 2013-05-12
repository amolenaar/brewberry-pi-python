
# Fake (test/reference, whatever you like) implementation for IO.
# It's a module: there's only one for the entire system.
import datetime

time = 0
temperature = 0
heater = Off

def read_time():
    return datetime.datetime.utcfromtimestamp(time)

def read_temperature():
    return temperature

def read_heater():
    return heater


# vim:sw=4:et:ai
