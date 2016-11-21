
from __future__ import absolute_import

from functools import partial
from .actors import ask


def topic_registry(receivers=(), register=None, deregister=None, which_receivers=None):
    if register:
        return partial(topic_registry, receivers=receivers + (register,))
    elif deregister:
        return partial(topic_registry, receivers=tuple(filter(lambda r: r is not deregister, receivers)))
    elif which_receivers:
        which_receivers(receivers)
    return partial(topic_registry, receivers=receivers)


def topic(topic_registry):
    def _topic(*args, **kwargs):
        receivers = ask(topic_registry, 'which_receivers')
        for r in receivers:
            r(*args, **kwargs)
        return _topic
    return _topic

