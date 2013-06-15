
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

    controller = Controller(io)
    sampler = Sampler(io, controller)

    log_file = open('session.log', 'a')
    log = Logger(sampler, json_appender(log_file))

    try:
        ioloop.PeriodicCallback(sampler, SAMPLER_INTERVAL, mainloop).start()
        ioloop.PeriodicCallback(controller, CONTROL_INTERVAL, mainloop).start()

        webui.setup(io, sampler, controller, mainloop)

        mainloop.start()
    finally:
        log_file.close()

# vim:sw=4:et:ai
