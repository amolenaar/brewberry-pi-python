
from tornado import ioloop
from eventconsumer import EventConsumers

INTERVAL = 5000
consumers = EventConsumers()

def read_temperature():
    temp = 20.00
    print 'read temp', temp
    consumers.notify(temperature=temp)

def register(mainloop):
    call = ioloop.PeriodicCallback(read_temperature, INTERVAL, mainloop)
    call.start()

# vim:sw=4:et:ai
