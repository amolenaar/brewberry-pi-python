
from brewberry.actors import spawn, init, spawn_self
import gevent.queue

def ping(self, queue, i):
    queue.put('ping %d' % i)
    if i == 0: return
    self(self, queue, i - 1)
    return pong

def pong(self, queue, i):
    queue.put('pong %d' % i)
    if i == 0: return
    self(self, queue, i - 1)
    return ping


def test_state_machine():

    def my_monitor(q):
        def catcher(e):
            q.put(e)
        return catcher

    response = gevent.queue.Queue()
    monitor_response = gevent.queue.Queue()

    state_machine = spawn_self(init, ping)
    state_machine.monitor(spawn(my_monitor, monitor_response))
    state_machine(state_machine, response, 5)

    assert response.get() == 'ping 5'
    assert response.get() == 'pong 4'
    assert response.get() == 'ping 3'
    assert response.get() == 'pong 2'
    assert response.get() == 'ping 1'

    assert monitor_response.get() == None


# vim:sw=4:et:ai
