"""
Flying Circus
-------------

GEvent based actors.

    
Future ideas:

 * How to deal with exceptions? Recover? Dead-letter queue? Supervision?
 * How does this work with state machines? generic/singledispatch?
 * Can we achieve n:m relationship between address and actor?
"""

import gevent
import gevent.queue


class PoisonPill(object):
    """
    Send this message to stop an actor.

    The Killer Joke, so to speak :).
    """


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
    Mailbox for actors. One mailbox per actor.

    This mailbox defines the communication protocol and some
    functional exceptions.
    """

    def __init__(self, maxsize=1024):
        self._inbox = gevent.queue.Queue(maxsize)

    def __iter__(self):
        return iter(self._inbox)

    def receive(self, timeout=None):
        """
        Receive a tuple (message, response_address).

        A NoMessage exception is raised if no message was received within the timeout.
        """
        try:
            return self._inbox.get(timeout=timeout)
        except (AttributeError, gevent.queue.Empty):
            raise NoMessage()

    def send(self, message, response_address=None):
        """
        Send a message. The response_address can be used to send back (or forward)
        a response provided by the actor.
        """
        try:
            return self._inbox.put_nowait((message, response_address))
        except (AttributeError, gevent.queue.Full):
            # Define strategy here: exception, dead letter queue, retry?
            raise UndeliveredMessage(message)

    def close(self):
        # This will raise AttributeError on every following invocation
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
            # Close the mailbox along with this greenlet
            mailbox.close()

    def actor():
        mailbox = Mailbox()
        gevent.spawn(actor_greenlet, func, mailbox)

        def address(message, response_address=None):
            """
            Send messages to the actor. Messages are sent to a mailbox
            and handled some time in the future.

            If no actor is present, an `ActorKilled` exception is raised.
            """
            mailbox.send(message, response_address)

        def ask(message, timeout=None):
            """
            Send message to an actor and await the response.
            This method assumes a single response to be returned.

            Optionally, provide a timeout (in seconds).
            """
            response_mailbox = Mailbox(1)
            address(message, response_mailbox.send)
            return response_mailbox.receive(timeout=timeout)[0]

        def kill():
            """
            Send the poison pill to the actor, terminating it.

            The actor logic does not have an option to do cleanup.
            """
            address(PoisonPill)

        address.ask = ask
        address.kill = kill

        return address

    return actor


# vim:sw=4:et:ai
