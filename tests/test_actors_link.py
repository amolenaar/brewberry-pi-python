
from brewberry.actors import spawn, link, monitor, kill
from gevent import sleep

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


# vim:sw=4:et:ai
