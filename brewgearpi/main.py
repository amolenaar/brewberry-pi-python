
import sys

import raspio
import logger
import webui

from tornado import ioloop

INTERVAL = 5000     # ms

def main():
    mainloop = ioloop.IOLoop.instance()

    log = logger.Logger(raspio, logger.json_appender(sys.stdout))
    ioloop.PeriodicCallback(log, INTERVAL, mainloop).start()

#    webui.register(mainloop)

    mainloop.start()


if __name__ == '__main__':
    main()

# vim:sw=4:et:ai
