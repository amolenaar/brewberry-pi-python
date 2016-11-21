"""
A timer actor.
"""
from __future__ import absolute_import

from .actors import with_self_address
import gevent


@with_self_address
def timer(self, receiver, kwargs=None, interval=3):
    gevent.sleep(interval)
    receiver(**(kwargs or {}))
    self(receiver, kwargs, interval)
    return timer

# vim: sw=4:ei:ai