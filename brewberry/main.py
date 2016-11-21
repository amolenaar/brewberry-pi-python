from gevent import monkey; monkey.patch_all()

from sampler import Sampler
from logger import Logger, SessionLogger
from controller import Controller
import webui
from actors import spawn, with_self_address, ask, ref
from supervisor import one_for_one_supervisor, child_spec
from functools import partial

import gevent, gevent.queue
from bottle import run

SAMPLER_INTERVAL = 2.000     # seconds
CONTROL_INTERVAL = 2.000


@with_self_address
def timer(self, receiver, kwargs=dict(), interval=3):
    gevent.sleep(interval)
    receiver(**kwargs)
    self(receiver, kwargs, interval)
    return timer


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


def start_system(io, log_appender=None):

    sup = spawn(one_for_one_supervisor, child_specs=(
        child_spec('controller', Controller, kwargs=dict(io=io), register=True),
        child_spec('controller-timer', timer, kwargs=dict(receiver=ref('controller'), kwargs=dict(tick=True), interval=CONTROL_INTERVAL)),
        child_spec('sample-topic-registry', topic_registry, register=True),
        child_spec('sample-topic', topic, kwargs=dict(topic_registry=ref('sample-topic-registry')), register=True),
        child_spec('sampler', Sampler, kwargs=dict(io=io, controller=ref('controller'), receiver=ref('sample-topic')), register=True),
        child_spec('sampler-timer', timer, kwargs=dict(receiver=ref('sampler')))
    ))

    gevent.sleep(0)

    log = spawn(Logger, log_appender) if log_appender else SessionLogger('session.log')
    ref('sample-topic-registry')(register=log)


def start_web():
    webui.setup_static()
    webui.setup_controls(ref('controller'))
    webui.setup_logger(ref('sample-topic-registry'))
    run(host='0.0.0.0', port=9080, server='gevent')


def main(io):
    start_system(io)
    start_web()


# vim:sw=4:et:ai
