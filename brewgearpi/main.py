
import sys

import logger
import webui

from tornado import ioloop

INTERVAL = 5000     # ms

def main(io):
    mainloop = ioloop.IOLoop.instance()

    log_file = open('session.log', 'a')
    try:
        log = logger.Logger(io, logger.json_appender(log_file))
        ioloop.PeriodicCallback(log, INTERVAL, mainloop).start()

        webui.setup(log, mainloop)

        mainloop.start()
    finally:
        log_file.close()

# vim:sw=4:et:ai
