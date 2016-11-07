
from brewberry.actor import actor, UndeliveredMessage
import gevent.queue
import pytest


@actor
def echo(message):
    return message


class Counter(object):
    def __init__(self, name):
        self.i = 0
        self.__name__ = name

    def __call__(self, message):
        self.i += 1
        return self.i


def test_defining_an_actor_should_not_start_it():
    assert echo.__name__ == 'actor:echo'


def test_actor_function_should_return_address():
    addr = echo()
    
    assert addr.__name__ == 'address:echo'
    addr.kill()


def test_killed_actor_throws_exception():
    addr = echo()
    addr.kill()

    # Allow actor to process the message:
    gevent.sleep(0)
    with pytest.raises(UndeliveredMessage):
        addr('should fail')


def test_actor_can_return_value():
    response = gevent.queue.Queue()
    addr = echo()
    addr('Hello', response_address=response.put)

    answer = response.get()

    assert answer == 'Hello'
    addr.kill()


def test_actor_can_return_value_via_ask():
    addr = echo()
    answer = addr.ask('Hello')

    assert answer == 'Hello'
    addr.kill()


def test_actor_can_send_message_to_itself():
    pass


def test_mailbox_is_tied_to_one_actor():
    actor1 = actor(Counter('1'))()
    actor2 = actor(Counter('2'))()

    for i in range(10):
        actor1(None)

    assert actor1.ask('a') == 11
    assert actor2.ask('b') == 1


def test_send_many_messages():
    addr = echo()
    with pytest.raises(UndeliveredMessage):
        for i in xrange(10000):
            addr(i)


# vim:sw=4:et:ai
