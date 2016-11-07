"""
Flying Circus
-------------

GEvent based actors.

"""

import gevent
import gevent.queue


class PoisonPill(object):
    """
    Send this message to stop an actor. The Killer Joke, so to speak :).
    """


class UndeliveredMessage(BaseException):
    """
    This exception is raised on an address if the actor
    no longer exists.
    """

    def __init__(self, message):
        BaseException.__init__(self)
        self.message = message


class Mailbox(object):
    """
    Mailbox for actors. One mailbox per actor.
    """

    def __init__(self, maxsize=1024):
        self._inbox = gevent.queue.Queue(maxsize)

    def __iter__(self):
        return iter(self._inbox)

    def get(self):
        return self._inbox.get()

    def put(self, message, response_address):
        try:
            return self._inbox.put_nowait((message, response_address))
        except (AttributeError, gevent.queue.Full):
            # Define strategy here: exception, dead letter queue, retry?
            raise UndeliveredMessage(message)

    def kill(self):
        self._inbox = None


def actor(func):
    """
    actor(func) -> actor
    actor() -> address

    The decorated function should have a format `func(message)`.

    The actor operator normalizes the function interface to (message, response_address=None)

    When the actor function is invoked, it spawns a new instance of the actor
    and returns it's "address".

    The Address references the actor and allows you to send messages to it.
    
    Send a PoisonPill to stop the actor.
    
    Ideas:
     * How to deal with exceptions? Recover? Dead-letter queue? Supervision?
     * How does this work with state machines? generic/singledispatch?
     * Can we achieve n:m relationship between address and actor?
    """

    def actor_greenlet(func, mailbox):
        try:
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
        finally:
            # Terminate mailbox along with this greenlet
            mailbox.kill()

    def actor():
        mailbox = Mailbox()
        gevent.spawn(actor_greenlet, func, mailbox)

        def address(message, response_address=None):
            """
            Send messages to the actor. Messages are sent to a mailbox
            and handled some time in the future.

            If no actor is present, an `ActorKilled` exception is raised.
            """
            mailbox.put(message, response_address)

        def ask(message):
            """
            Send message to an actor and await the response.

            TODO: timeouts
            """
            response_queue = gevent.queue.Queue(1)
            address(message, response_queue.put_nowait)
            return response_queue.get()

        def kill():
            """
            Send the poison pill to the actor.
            """
            address(PoisonPill)

        address.ask = ask
        address.kill = kill
        address.__name__ = 'address:' + func.__name__
        address.__doc__ = func.__doc__

        return address

    actor.__name__ = 'actor:' + func.__name__
    actor.__doc__ = func.__doc__

    return actor


# vim:sw=4:et:ai
