from gevent import monkey; monkey.patch_all()

from sampler import Sampler
from logger import Logger, json_appender
from controller import Controller
import webui
from actors import spawn, with_self_address, ask
from functools import partial

import gevent, gevent.queue
from bottle import run

SAMPLER_INTERVAL = 5.000     # seconds
CONTROL_INTERVAL = 2.000


@with_self_address
def timer(self, receiver, kwargs=dict(), interval=CONTROL_INTERVAL):
    gevent.sleep(interval)
    receiver(**kwargs)
    self(receiver, kwargs, interval)
    return timer


def topic_registry(receivers=(), register=None, deregister=None, query_receivers=None):
    if register:
        return partial(topic_registry, receivers=receivers + (register,))
    elif deregister:
        return partial(topic_registry, receivers=tuple(filter(lambda r: r is not deregister, receivers)))
    elif query_receivers:
        query_receivers(receivers)
    return partial(topic_registry, receivers=receivers)


def topic(topic_registry):
    def _topic(*args, **kwargs):
        receivers = ask(topic_registry, 'query_receivers')
        for r in receivers:
            r(*args, **kwargs)
        return _topic
    return _topic


def start_system(io, log_appender):
    log = spawn(Logger, log_appender)
    controller = spawn(Controller, io)
    controller_timer = spawn(timer, receiver=controller, kwargs=dict(tick=True), interval=CONTROL_INTERVAL)

    sample_topic_registry = spawn(topic_registry)
    sample_topic = spawn(topic, sample_topic_registry)

    sampler = spawn(Sampler, io, controller, receiver=sample_topic)
    sample_timer = spawn(timer, receiver=sampler, kwargs=dict(io=io, controller=controller, receiver=sample_topic))

    # Put all on a one_for_all supervisor
    sample_topic_registry(register=log)

    return controller, sample_topic_registry


def main(io):
    log_file = open('session.log', 'a')

    try:
        controller, sample_topic_registry = start_system(io, json_appender(log_file))
        webui.setup_static()
        webui.setup_controls(controller)
        webui.setup_logger(sample_topic_registry)
        run(host='0.0.0.0', port=9080, server='gevent')

    finally:
        log_file.close()

# vim:sw=4:et:ai
