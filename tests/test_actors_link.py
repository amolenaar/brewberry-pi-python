
from brewberry.actors import spawn, spawn_link, link, monitor, kill
from gevent import sleep
from gevent.queue import Queue


def test_link_two_actors():

    def repeater1():
        return repeater1

    def repeater2():
        print 'linking actor 1 to actor 2'
        link(actor1)
        return repeater1

    actor1 = spawn(repeater1)
    actor2 = spawn(repeater2)

    dead_procs = []

    def mon():
        def monitor_actor(f, e):
            dead_procs.append(f)
        return monitor_actor

    monitor(actor1, spawn(mon))
    monitor(actor2, spawn(mon))

    kill(actor1)

    sleep(0.1)

    assert repeater1 in dead_procs, dead_procs
    assert repeater2 in dead_procs, dead_procs


def test_link_chain():
    def countdown(counter):
        spawn_link(countdown, counter - 1)
        if counter <= 0: raise Exception('end')
        sleep(1)

    caught_exceptions = Queue()

    def supervise(f, e):
        caught_exceptions.put(e)

    addr = spawn(countdown, 10)
    monitor(addr, supervise)

    # wait for
    assert repr(caught_exceptions.get(timeout=2)) == 'KilledByLink()'


def test_link_chain_ending_normally_child_first():
    def countdown(counter):
        if counter > 0:
            spawn_link(countdown, counter - 1)
        sleep(0.1 * counter)

    caught_exceptions = Queue()

    def supervise(f, e):
        caught_exceptions.put(e)

    addr = spawn(countdown, 10)
    monitor(addr, supervise)

    assert repr(caught_exceptions.get(timeout=2)) == 'None'


def test_link_chain_ending_normally_parent_first():
    def countdown(counter):
        if counter > 0:
            spawn_link(countdown, counter - 1)
        sleep(1 - (counter/10.))

    caught_exceptions = Queue()

    def supervise(f, e):
        caught_exceptions.put(e)

    addr = spawn(countdown, 10)
    monitor(addr, supervise)

    assert repr(caught_exceptions.get(timeout=2)) == 'None'

# vim:sw=4:et:ai
