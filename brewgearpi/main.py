
from __future__ import absolute_import

from tornado import ioloop

import temperature
import webui

modules = [
    temperature,
    webui
    ]

def main():
    mainloop = ioloop.IOLoop.instance()
    for mod in modules:
        mod.register(mainloop)
    mainloop.start()

if __name__ == '__main__':
    main()

# vim:sw=4:et:ai
