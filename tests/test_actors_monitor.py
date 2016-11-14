
from brewberry.actors import spawn, with_self_address, monitor, kill
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

    def countdown(counter):
        if counter <= 0: raise Exception("end")

    caught_exceptions = []

    # See http://learnyousomeerlang.com/supervisors
    @with_self_address
    def supervisor(self, func, counter=10):
        def supervise(f, e):
            if not e:
                self(func, counter - 1)
            else:
                caught_exceptions.append(str(e))
        addr = spawn(func, counter)
        monitor(addr, supervise)
        return supervisor

    s = spawn(supervisor, countdown)

    sleep(0.1)

    kill(s)

    assert 'end' in caught_exceptions, caught_exceptions


# vim:sw=4:et:ai
