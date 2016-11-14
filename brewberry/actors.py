"""
Flying Circus
-------------

GEvent based actors.

This library tries to stay true to Erlang's way of handling actors.

Sources:
 
 * http://berb.github.io/diploma-thesis/community/054_actors.html - for the actor concepts
 * http://learnyousomeerlang.com - 
 * http://erlang.org/doc/reference_manual/errors.html
 * http://erlang.org/doc/reference_manual/processes.html.

Still need implementation for:

 * @trap_exit - do not kill, but pass on the exception to the actor
 * spawn_monitor(func) -> (addr(), monitor_ref)
 * exit(addr, reason) -> None - let the actor die with a reason (raise it)
 * provide a simple OO bridge. e.g. allow ``address.message(args)``
"""

from collections import namedtuple
import gevent
from gevent.queue import Queue

MAX_QUEUE_SIZE = 1024


KillerJoke = intern('KillerJoke')
Monitor = intern('Monitor')
Link = intern('Link')
TrapLink = intern('TrapLink')
ActorInfo = intern('ActorInfo')

ActorInfoTuple = namedtuple('ActorInfoTuple', ['links', 'mailbox_size', 'monitored_by', 'monitors', 'running', 'successful', 'exception', 'exc_info'])

class Killed(Exception):
    """
    Raised if an actor is killed.
    """
    pass


class KilledByLink(Killed):
    """
    Special case of being killed by a dead link
    """
    pass


class UndeliveredMessage(Exception):
    """
    This exception is raised on an address if the actor
    mailbox is full.
    """

def with_self_address(func):
    """
    >>> @with_self_address
    ... def run_forever(self_addr):
    ...     self_addr()
    ...     return run_forever

    To ensure the actor's own address is passed in, apply this decorator.

    :param func:
    :return:
    """
    func.with_self_address = True
    return func


def spawn(func, *args, **kwargs):
    """
    spawn(func, *args, **kwargs) -> address

    Start a new actor by invoking the function ``func(*args, **kwargs)``.
    The function should return the function to be invoked when the next
    message arrives.

    The address is a simple callable on which you can send the new message::

      address(*args, **kwargs) -> address
    
    If the function should send messages to itself, decorate your function
    with ``@with_self_address``.
    """

    mailbox = Queue(MAX_QUEUE_SIZE)

    def actor_process(func):
        next_func = func
        for args, kwargs in mailbox:
            if getattr(next_func, 'with_self_address', False):
                args = (address,) + args
            next_func = next_func(*args, **kwargs)
            if not next_func:
                break

    # should we consider calling spawn_raw() instead?
    proc = gevent.spawn(actor_process, func)

    def address(*args, **kwargs):
        """
        address(*args, **kwargs) -> address | actor_info

        Send messages to the actor. Messages are sent to a mailbox
        and handled some time in the future.

        If there is no actor alive to handle the request, it it simply ignored.
        """
        try:
            # Special cases: this allows us to get feedback on processes that are already done
            if Monitor in args:
                mon = kwargs['monitor']
                proc.link(lambda dead_proc: mon(func, dead_proc.exception))
            elif Link in args:
                me = gevent.getcurrent()
                me.link_exception(lambda p: proc.kill(KilledByLink))
                proc.link_exception(lambda p: me.kill(KilledByLink))
            elif TrapLink in args:
                me = gevent.getcurrent()
                me.link_exception(lambda dead_proc: proc.kill(KilledByLink))
                proc.link_exception(lambda dead_proc: me._address(trap_exit=(address, dead_proc.exception)))
            elif ActorInfo in args:
                return ActorInfoTuple(
                    links=(),
                    mailbox_size=mailbox.qsize(),
                    monitored_by=(),
                    monitors=(),
                    running=not proc.ready(),
                    successful=proc.successful(),
                    exception=proc.exception,
                    exc_info=proc.exc_info
                )
            elif KillerJoke in args:
                proc.kill(Killed)
            else:
                mailbox.put_nowait((args, kwargs))
        except gevent.queue.Full:
            raise UndeliveredMessage()
        return address

    proc._address = address
    address.__name__ = 'address:{}'.format(func)

    return address(*args, **kwargs)


def spawn_link(func, *args, **kwargs):
    """
    spawn_link(func, *args, **kwargs) -> address

    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    address = spawn(func, Link)
    return address(*args, **kwargs)

def spawn_trap_link(func, *args, **kwargs):
    """
    spawn_trap_link(func, *args, **kwargs) -> address

    Like ``spawn_link()``, but if the child actor dies, the exception
    is sent to the current actor in the form::

      addr(trap_exit=(func, exc))

    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    address = spawn(func, TrapLink)
    return address(*args, **kwargs)


def ask(address, query, timeout=1):
    """
    ask(address, query, timeout=1) -> any

    Query a value on an actor. The query is sent to a named parameter
    where the name equals the value of ``query``.

    >>> def actor(query_field=None):
    ...     if query_field:
    ...         query_field(42)
    ...         return # terminate after the answer is delivered
    ...     return actor

    >>> address = spawn(actor)
    >>> ask(address, 'query_field')
    42

    :param address: Actor address
    :param query: String of the query value to retrieve.
    :param timeout: how long to wait. Default is 1 second.
    :return: Value requested from the actor
    """
    response_queue = Queue(1)
    address(**{query: response_queue.put})
    return response_queue.get(timeout=timeout)


def link(address):
    """
    link(address) -> None

    Create link between the calling actor and the actor identified by it's address

    :param address: Address of the actor to link to
    :return: nothing
    """
    return address(Link)


def monitor(address, mon):
    """
    monitor(address, mon) -> address

    TODO: change output to monitor_ref

    Add a monitor to this actor. The monitor is called with the
    exception as argument, or None if the actor ended with no exception.

    ``mon`` may be an actor address or a function.
    It's called from a separate greenlet anyway.
    """
    return address(Monitor, monitor=mon)


def actor_info(address):
    """
    actor_info(address) -> { running: bool, ... }

    This function provides everything you want to know about the actor, and more
    """
    return address(ActorInfo)


def kill(actor):
    """
    kill(actor) -> actor

    Send the Killer Joke to the actor, terminating it.

    The actor logic does not have an option to do cleanup.
    """
    return actor(KillerJoke)


# vim:sw=4:et:ai
