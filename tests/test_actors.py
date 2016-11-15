
from brewberry.actors import spawn, ask, kill, actor_info, UndeliveredMessage
import gevent.queue
import pytest


def echo(message, queue):
    queue.put(message)
    return echo


class Counter(object):
    def __init__(self):
        self.i = 0

    def __call__(self, ask=None):
        if ask:
            ask.put(self.i)
        else:
            self.i += 1
        return self



def test_actor_function_should_return_address():
    addr = spawn(echo, 'Hello', gevent.queue.Queue())
    
    assert addr.__name__.startswith('address:<'), addr.__name__
    kill(addr)


def test_killed_actor_throws_exception():
    addr = spawn(echo, 'Hello', gevent.queue.Queue())
    kill(addr)

    # Allow actor to process the message:
    gevent.sleep(0)

    # Message is refused:
    addr('should fail')


def test_actor_can_return_value():
    response = gevent.queue.Queue()
    echo_ref = spawn(echo, 'Hello', response)
    echo_ref('World', response)

    assert response.get() == 'Hello'
    assert response.get() == 'World'

    kill(echo_ref)


def test_mailbox_is_tied_to_one_actor():
    response = gevent.queue.Queue()
    actor1 = spawn(Counter())
    actor2 = spawn(Counter())

    for i in range(10):
        actor1()

    actor1(ask=response)
    assert response.get() == 11

    actor2(ask=response)
    assert response.get() == 1


def test_send_many_messages():
    def noop():
        return noop
    addr = spawn(noop)
    with pytest.raises(UndeliveredMessage):
        for i in xrange(10000):
            addr()


def test_actor_does_not_break_on_invalid_message_signature():

    def noop():
        return noop
    addr = spawn(noop)

    addr(invalid=1)

    gevent.sleep(0)

    assert actor_info(addr).running

    kill(addr)

    assert not actor_info(addr).running

def test_ask():
    def ask_me():
        def real_ask_me(q):
            q(42)
        return real_ask_me

    ask_me_addr = spawn(ask_me)
    answer = ask(ask_me_addr, 'q')

    assert answer == 42

# vim:sw=4:et:ai
