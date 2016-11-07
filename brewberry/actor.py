"""
Flying Circus
-------------

GEvent based actors.

    
Future ideas:

 * How to deal with exceptions? Recover? Dead-letter queue? Supervision?
 * How does this work with state machines? generic/singledispatch?
 * Can we achieve n:m relationship between address and actor?

Erlang's spawn has the following signature:
spawn(Module, Exported_Function, List of Arguments)

So spawn(callable, *args, **kwargs) is 
"""

import gevent
import gevent.queue


class Atom(object):
    """
    A unique token.
    """
    def __init__(self, doc=None):
        self.__doc__ = doc


PoisonPill = Atom("Send this message to stop an actor. The Killer Joke, so to speak :).")


class UndeliveredMessage(Exception):
    """
    This exception is raised on an address if the actor
    no longer exists.
    """

    def __init__(self, message):
        BaseException.__init__(self)
        self.message = message


class NoMessage(Exception):
    """
    This exception is raised if no messages are received.
    """


class Mailbox(object):
    """
    Mailbox for actors.

    This mailbox defines the communication protocol and some
    functional exceptions.
    """

    def __init__(self, maxsize=1024):
        self._inbox = gevent.queue.Queue(maxsize)

    def __iter__(self):
        return self

    def next(self):
        if not self._inbox:
            raise StopIteration
        message = self.receive()
        if message is PoisonPill:
            raise StopIteration
        return message

    def receive(self, timeout=None):
        """
        Receive a tuple (message, response_address).

        A NoMessage exception is raised if no message was received within the timeout.
        """
        try:
            return self._inbox.get(timeout=timeout)
        except (AttributeError, gevent.queue.Empty):
            raise NoMessage()

    def send(self, message):
        """
        Send a message. The response_address can be used to send back (or forward)
        a response provided by the actor.
        """
        try:
            return self._inbox.put_nowait(message)
        except (AttributeError, gevent.queue.Full):
            # Define strategy here: exception, dead letter queue, retry?
            raise UndeliveredMessage(message)

    def close(self):
        # This will raise AttributeError on every following invocation
        self._inbox = None


def actor(func, *args, **kwargs):
    """
    actor(func, *ags, **kwargs) -> address

    The actor operator normalizes the function interface to (message, response_address=None)

    When the actor function is invoked, it spawns a new instance of the actor
    and returns it's "address".

    The Address references the actor and allows you to send messages to it.
    
    Send a PoisonPill to stop the actor.
    """

    mailbox = Mailbox()

    def actor_greenlet(func):
        try:
            for args, kwargs in mailbox:
                func = func(*args, **kwargs)
                if not func:
                    break
        finally:
            # Close the mailbox along with this greenlet
            mailbox.close()

    gevent.spawn(actor_greenlet, func)

    def address(*args, **kwargs):
        """
        Send messages to the actor. Messages are sent to a mailbox
        and handled some time in the future.

        If no actor is present, an `ActorKilled` exception is raised.
        """
        mailbox.send((args, kwargs))

    def kill():
        """
        Send the poison pill to the actor, terminating it.

        The actor logic does not have an option to do cleanup.
        """
        mailbox.send(PoisonPill)

    address.kill = kill

    address(*args, **kwargs)

    return address


# vim:sw=4:et:ai
