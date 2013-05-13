
import sys

import logger
import webui

from tornado import ioloop

INTERVAL = 5000     # ms

def main(io):
    mainloop = ioloop.IOLoop.instance()

    log = logger.Logger(io, logger.json_appender(sys.stdout))
    ioloop.PeriodicCallback(log, INTERVAL, mainloop).start()

    webui.setup(log, mainloop)

    mainloop.start()


# vim:sw=4:et:ai
