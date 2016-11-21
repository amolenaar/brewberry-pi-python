from gevent import monkey; monkey.patch_all()

from sampler import Sampler
from logger import Logger, SessionLogger
from controller import Controller
import webui
from actors import spawn, monitor, ref
from supervisor import one_for_one_supervisor, child_spec
from topic import topic, topic_registry
import gevent, gevent.queue
from bottle import run


def start_system(io, log_appender=None):

    sup = spawn(one_for_one_supervisor, child_specs=(
        child_spec('sample-topic-registry', topic_registry, register=True),
        child_spec('sample-topic', topic, kwargs=dict(topic_registry=ref('sample-topic-registry')), register=True),
        child_spec('controller', Controller, kwargs=dict(io=io), register=True),
        child_spec('sampler', Sampler, kwargs=dict(io=io, controller=ref('controller'), receiver=ref('sample-topic')), register=True)
    ))

    monitor(sup, lambda f, e: exit(1 if e else 0))

    gevent.sleep(0)

    log = spawn(Logger, log_appender) if log_appender else spawn(SessionLogger, 'session.log')
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
