
from brewberry.actor import actor, UndeliveredMessage
import gevent.queue
import pytest


def echo(message, queue):
    queue.put(message)
    return echo

# A two function state machine
def ping_init():
    return ping

def ping(receive, queue, i):
    queue.put('ping %d' % i)
    if i == 0: return
    receive(receive, queue, i-1)
    return pong

def pong(receive, queue, i):
    queue.put('pong %d' % i)
    if i == 0: return
    receive(receive, queue, i-1)
    return ping


class Counter(object):
    def __init__(self):
        self.i = 0

    def __call__(self, message):
        self.i += 1
        return self.i



def test_actor_function_should_return_address():
    addr = actor(echo, 'Hello', gevent.queue.Queue())
    
    assert addr.__name__ == 'address'
    addr.kill()


def test_killed_actor_throws_exception():
    addr = actor(echo, 'Hello', gevent.queue.Queue())
    addr.kill()

    # Allow actor to process the message:
    gevent.sleep(0)
    with pytest.raises(UndeliveredMessage):
        addr('should fail')


def test_actor_can_return_value():
    response = gevent.queue.Queue()
    echo_ref = actor(echo, 'Hello', response)
    echo_ref('World', response)

    assert response.get() == 'Hello'
    assert response.get() == 'World'

    echo_ref.kill()


def test_can_change_state():
    response = gevent.queue.Queue()
    ping_ref = actor(ping_init)
    ping_ref(ping_ref, response, 5)

    assert response.get() == 'ping 5'
    assert response.get() == 'pong 4'
    assert response.get() == 'ping 3'
    assert response.get() == 'pong 2'
    assert response.get() == 'ping 1'

    # Actor ended by itself:
    with pytest.raises(UndeliveredMessage):
        ping_ref.kill()


def xtest_mailbox_is_tied_to_one_actor():
    actor1 = actor(Counter())
    actor2 = actor(Counter())

    for i in range(10):
        actor1(i)

    assert actor1.ask('a') == 11
    assert actor2.ask('b') == 1


def test_send_many_messages():
    def noop():
        return noop
    addr = actor(noop)
    with pytest.raises(UndeliveredMessage):
        for i in xrange(10000):
            addr(i)


# vim:sw=4:et:ai
