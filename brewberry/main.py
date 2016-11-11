from gevent import monkey; monkey.patch_all()
import bottle

from sampler import Sampler
from logger import Logger, json_appender
from controller import Controller
import webui
from actors import spawn, spawn_self, ask
from functools import partial

import gevent, gevent.queue
from bottle import run

SAMPLER_INTERVAL = 5.000     # seconds
CONTROL_INTERVAL = 2.000


def timer(self, receiver, kwargs=dict(), interval=CONTROL_INTERVAL):
    gevent.sleep(interval)
    receiver(**kwargs)
    self(receiver, kwargs, interval)
    return timer


def topic_registry(receivers=(), register=None, deregister=None, query_receivers=None):
    if register is not None:
        return partial(topic_registry, receivers=receivers + (register,))
    elif deregister is not None:
        return partial(topic_registry, receivers=tuple(filter(lambda r: r is not deregister, receivers)))
    elif query_receivers is not None:
        query_receivers(receivers)
    return partial(topic_registry, receivers=receivers)


def topic(topic_registry):
    def _topic(*args, **kwargs):
        receivers = ask(topic_registry, 'query_receivers')
        print 'topic', receivers, args, kwargs
        for r in receivers:
            r(*args, **kwargs)
        return _topic
    return _topic


def main(io):
    log_file = open('session.log', 'a')
    log = spawn(Logger, json_appender(log_file))

    try:
        controller = spawn(Controller, io)
        controller_timer = spawn_self(timer, receiver=controller, kwargs=dict(tick=True), interval=CONTROL_INTERVAL)

        sample_topic_registry = spawn(topic_registry)
        sample_topic = spawn(topic, sample_topic_registry)

        sampler = spawn(Sampler, io, controller, receiver=sample_topic)
        sample_timer = spawn_self(timer, receiver=sampler, kwargs=dict(io=io, controller=controller, receiver=sample_topic))

        sample_topic_registry(register=log)

        webui.setup_static()
        webui.setup_controls(controller)
        webui.setup_logger(sample_topic_registry)
        run(host='0.0.0.0', port=9080, server='gevent')

    finally:
        log_file.close()

# vim:sw=4:et:ai
