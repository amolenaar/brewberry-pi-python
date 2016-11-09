"""
Flying Circus
-------------

GEvent based actors.
    
Future ideas:

 * How does this work with state machines? generic/singledispatch?
 * Can we achieve n:m relationship between address and actor?

This library tries to stay true to Erlang's way of handling actors.

See http://erlang.org/doc/reference_manual/errors.html
and http://erlang.org/doc/reference_manual/processes.html.

"""

import functools
import gevent
import gevent.queue

MAX_QUEUE_SIZE = 1024


class atom(object):
    """
    A unique identifier throughout the application.
    """
    def __init__(self, doc=None):
        self.__doc__ = doc


PoisonPill = atom("Send this message to stop an actor. The Killer Joke, so to speak :).")

class Killed(Exception):
    """
    Raised if an actor is killed.
    """
    pass

class UndeliveredMessage(Exception):
    """
    This exception is raised on an address if the actor
    mailbox is full.
    """


def spawn(func, *args, **kwargs):
    """
    spawn(func, *ags, **kwargs) -> address

    Start a new actor by invoking the function `func(*args, **kwargs)`.
    The function should return the function to be invoked when the next message arrives.

    The address is a simple callable on which you can send the new message

    address(*args, **kwargs) -> None
    
    Invoke `address.kill()` to stop the actor. Messages in the queue are handled up to
    this message.

    If the function should send messages to itself, use ``spawn_self`` instead.
    """

    mailbox = gevent.queue.Queue(MAX_QUEUE_SIZE)

    def actor_process(func):
        for args, kwargs in mailbox:
            if args == (PoisonPill,):
                raise Killed
            func = func(*args, **kwargs)
            if not func:
                break

    proc = gevent.spawn(actor_process, func)

    def address(*args, **kwargs):
        """
        Send messages to the actor. Messages are sent to a mailbox
        and handled some time in the future.

        If there is no actor alive to handle the request, it it simply ignored.
        """
        if not proc.ready():
            try:
                mailbox.put_nowait((args, kwargs))
            except gevent.queue.Full:
                raise UndeliveredMessage()
        return address

    def kill():
        """
        Send the poison pill to the actor, terminating it.

        The actor logic does not have an option to do cleanup.
        """
        address(PoisonPill)

    def monitor(mon):
        """
        Add a monitor to this actor. The monitor is called with the
        exception as argument, or None if the actor ended with no exception.
        """
        proc.link(lambda dead_proc: mon(dead_proc.exception))
        return address

    address.kill = kill
    address.monitor = monitor

    address(*args, **kwargs)

    return address


def spawn_self(func, *args, **kwargs):
    """
    Spawn an actor with a self-reference as first parameter.

    `func(self_addr, *args, **kwargs)`

    This will return a partially applied function, so the user
    does not have to bother with the function address itself.
    """
    func_addr = spawn(lambda f: f, func)

    def address(*args, **kwargs):
        func_addr(address, *args, **kwargs)
        return address

    def monitor(mon):
        func_addr.monitor(mon)
        return address

    address.monitor = monitor
    address.kill = func_addr.kill

    address(*args, **kwargs)

    return address


# vim:sw=4:et:ai
