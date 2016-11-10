
from brewberry.actors import spawn, spawn_self, monitor, kill
from gevent.queue import Queue
from gevent import sleep


def die_fast():
    raise Exception("Die fast")


def my_monitor(q):
    def catcher(f, e):
        q.put((f, e))
    return catcher


def test_monitor_on_actor():
    p = spawn(die_fast)

    monitor_response = Queue()
    monitor(p, spawn(my_monitor, monitor_response))

    f, e = monitor_response.get()
    assert f is die_fast
    assert str(e) == 'Die fast'


def test_monitor_on_dead_actor():
    p = spawn(die_fast)

    sleep(0)

    monitor_response = Queue()
    monitor(p, spawn(my_monitor, monitor_response))

    f, e = monitor_response.get()
    assert f is die_fast
    assert str(e) == 'Die fast'


def test_supervision():

    def echo(counter):
        print counter
        if counter > 9: raise Exception("end")

    # See http://learnyousomeerlang.com/supervisors
    def restarter(self, func, counter=0):
        def supervise(f, e):
            if not e:
                self(f, counter + 1)
            else:
                print 'Caught error', e
        monitor(spawn(func, counter), supervise)
        return restarter

    supervisor = spawn_self(restarter, echo)

    sleep(0.1)

    kill(supervisor)

# vim:sw=4:et:ai
