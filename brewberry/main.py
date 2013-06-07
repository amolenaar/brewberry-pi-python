
import sys

from sampler import Sampler
from logger import Logger, json_appender
from controller import Controller
import webui

from tornado import ioloop

SAMPLER_INTERVAL = 5000     # ms
CONTROL_INTERVAL = 2000

def main(io):
    mainloop = ioloop.IOLoop.instance()

    sampler = Sampler(io)
    log_file = open('session.log', 'a')
    log = Logger(sampler, json_appender(log_file))

    control = Controller(io)
    try:
        ioloop.PeriodicCallback(sampler, SAMPLER_INTERVAL, mainloop).start()
        ioloop.PeriodicCallback(control, CONTROL_INTERVAL, mainloop).start()

        webui.setup(io, sampler, control, mainloop)

        mainloop.start()
    finally:
        log_file.close()

# vim:sw=4:et:ai
