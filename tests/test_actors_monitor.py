
from brewberry.actors import spawn, spawn_self
from gevent.queue import Queue
from gevent import sleep

def die_fast():
    raise Exception("Die fast")

def my_monitor(q):
    def catcher(e):
        q.put(e)
    return catcher


def test_monitor_on_actor():
    p = spawn(die_fast)

    monitor_response = Queue()
    p.monitor(spawn(my_monitor, monitor_response))

    assert str(monitor_response.get()) == 'Die fast'


def test_monitor_on_dead_actor():
    p = spawn(die_fast)

    sleep(0)

    monitor_response = Queue()
    p.monitor(spawn(my_monitor, monitor_response))

    assert str(monitor_response.get()) == 'Die fast'


def test_supervision():

    def echo(counter):
        print counter
        if counter > 9: raise Exception("end")

    def restarter(self, func, counter=0):
        def supervise(e):
            if not e:
                self(func, counter + 1)
            else:
                print 'Caught error', e
        spawn(func, counter).monitor(supervise)
        return restarter

    supervisor = spawn_self(restarter, echo)

    sleep(0.1)

    supervisor.kill()

# vim:sw=4:et:ai
