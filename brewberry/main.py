
import sys

from sampler import Sampler
from logger import Logger, json_appender
import webui

from tornado import ioloop

INTERVAL = 5000     # ms

def main(io):
    mainloop = ioloop.IOLoop.instance()

    sampler = Sampler(io)
    log_file = open('session.log', 'a')
    try:
        log = Logger(sampler, json_appender(log_file))
        ioloop.PeriodicCallback(sampler, INTERVAL, mainloop).start()

        webui.setup(sampler, mainloop)

        mainloop.start()
    finally:
        log_file.close()

# vim:sw=4:et:ai
