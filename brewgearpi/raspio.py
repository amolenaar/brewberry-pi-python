#
# IO stuff, on the Raspberry Pi.
#

HEATING_PIN = 18

import os, glob, datetime, time

import RPi.GPIO as io
io.setmode(io.BCM)
io.setup(HEATING_PIN, io.OUT)

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def _read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def _read_temp():
    lines = _read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = _read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

_heating = Off

## Interface methods:

def read_time():
    return datetime.datetime.fromtimestamp(time.time())

def read_temperature():
    return _read_temp()

def read_heating():
    return _heating

def set_heating(v):
    global _heating
    io.output(HEATING_PIN, v)
    _heating = v


def init():
    set_heating(_heating)


init()

# vim: sw=4:et:ai
