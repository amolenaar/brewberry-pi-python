"""
GEvent based actors

See http://sdiehl.github.io/gevent-tutorial/#actors
"""

import gevent
import gevent.queue


class PoisonPill(object):
    """
    Send this message to stop an actor.
    """
    pass


class ActorKilled(BaseException):
    """
    This exception is raised on an address if the actor
    no longer exists.
    """
    pass


def actor(func):
    """
    actor(func) -> address

    The decorated function should have a format `func(message)`.

    The actor operator normalizes the function interface to (message, response_address=None)

    When the actor function is invoked, it spawns a new instance of the actor
    and returns it's "address".

    The Address references the actor and allows you to send messages to it.
    
    Send a PoisonPill to stop the actor.
    
    Ideas:
     * How to deal with exceptions?
     * How does this work with state machines? generic/singledispatch?
     * Can we achieve n:m relationship between address and actor?
    """
    mailbox = gevent.queue.Queue()

    def actor_greenlet():
        for message, response_address in mailbox:
            if message is PoisonPill:
                break
            try:
                response = func(message)
            except BaseException, e:
                response = e
            finally:
                if response_address:
                    response_address(response)

    def address(message, response_address=None):
        #if not address.__greenlet__.started:
        #    raise ActorKilled()
        mailbox.put((message, response_address))

    def ask(message):
        """
        Send message to an actor and await the response.
        """
        response_address = gevent.queue.Queue()
        address(message, response_address.put)
        return response_address.get()

    address.ask = ask
    address.__name__ = 'address:' + func.__name__
    address.__doc__ = func.__doc__

    def actor():
        gevent.spawn(actor_greenlet)
        return address

    actor.__name__ = 'actor:' + func.__name__
    actor.__doc__ = func.__doc__

    return actor


# vim:sw=4:et:ai
