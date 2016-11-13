"""
Flying Circus
-------------

GEvent based actors.

We try to:
 * Leverage actor interaction by using named parameters

Future ideas:

 * How does this work with state machines? generic/singledispatch?
 * Can we achieve n:m relationship between address and actor?

This library tries to stay true to Erlang's way of handling actors.

See http://erlang.org/doc/reference_manual/errors.html
and http://erlang.org/doc/reference_manual/processes.html.

Still need implementation for:

 * link(address) -> None - Create link between the calling actor and the actor identified by it's address
 * spawn_link(func) -> addr() (with _self version?)
 * spawn_monitor(func) -> (addr(), monitor_addr())
 * exit(addr, reason) -> None - let the actor die with a reason (raise it)
 * convert spawn_self's "self" part to be a decorator?
"""

import gevent
from gevent.queue import Queue

MAX_QUEUE_SIZE = 1024


class atom(object):
    """
    A unique identifier throughout the application.
    """
    def __init__(self, doc=None):
        self.__doc__ = doc


KillerJoke = atom("Send this message to stop an actor.")
Monitor = atom("Create a monitor on the actor")
Link = atom("Create a dead or alive link between two actors")


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

    Start a new actor by invoking the function ``func(*args, **kwargs)``.
    The function should return the function to be invoked when the next message arrives.

    The address is a simple callable on which you can send the new message::

      address(*args, **kwargs) -> address
    
    Invoke `'kill(address)`` to stop the actor. Messages in the queue are handled up to
    this message.

    If the function should send messages to itself, use ``spawn_self`` instead.
    """

    mailbox = Queue(MAX_QUEUE_SIZE)

    def actor_process(func):
        next_func = func
        for args, kwargs in mailbox:
            if KillerJoke in args:
                raise Killed
            else:
                next_func = next_func(*args, **kwargs)
                if not next_func:
                    break

    # should we consider calling spawn_raw() instead?
    proc = gevent.spawn(actor_process, func)

    def address(*args, **kwargs):
        """
        Send messages to the actor. Messages are sent to a mailbox
        and handled some time in the future.

        If there is no actor alive to handle the request, it it simply ignored.

        TODO: Create an object to allow specific messages to be sent as ``actor.message(args)``
        """
        try:
            # Special case: this allows us to get feedback on processes that are already done
            if Monitor in args:
                mon = kwargs['monitor']
                proc.link(lambda dead_proc: mon(func, dead_proc.exception))
            elif Link in args:
                me = gevent.getcurrent()
                print 'building link between', proc, me
                me.link(lambda p: proc.throw(Killed))
                proc.link(lambda p: me.throw(Killed))
            else:
                mailbox.put_nowait((args, kwargs))
        except gevent.queue.Full:
            raise UndeliveredMessage()
        return address

    address(*args, **kwargs)

    return address


def spawn_self(func, *args, **kwargs):
    """
    spawn_self(func, *args, **kwargs) -> address

    Spawn an actor with a self-reference as first parameter::

      func(self_addr, *args, **kwargs)

    This will return a partially applied function, so the user
    does not have to bother with the function address itself.
    """
    def address(*args, **kwargs):
        actor(address, *args, **kwargs)
        return address

    actor = spawn(func, address, *args, **kwargs)
    address.__doc__ = actor.__doc__

    return address

def ask(actor, query, timeout=1):
    response_queue = Queue(1)
    actor(**{query: response_queue.put})
    return response_queue.get(timeout=timeout)


def link(address):
    """
    link(address) -> None

    Create link between the calling actor and the actor identified by it's address

    :param address: Address of the actor to link to
    :return: nothing
    """
    return address(Link)


def monitor(actor, mon):
    """
    monitor(actor, mon) -> actor

    TODO: change output to monitor_ref

    Add a monitor to this actor. The monitor is called with the
    exception as argument, or None if the actor ended with no exception.
    """
    return actor(Monitor, monitor=mon)


def kill(actor):
    """
    kill(actor) -> actor

    Send the Killer Joke to the actor, terminating it.

    The actor logic does not have an option to do cleanup.
    """
    return actor(KillerJoke)


# vim:sw=4:et:ai
