from gevent import monkey; monkey.patch_all()

from sampler import sample
from logger import Logger, json_appender
from controller import Controller
import webui

import gevent, gevent.queue
from bottle import run

import bottle
bottle.debug(True)

SAMPLER_INTERVAL = 5.000     # seconds
CONTROL_INTERVAL = 2.000


def timer_loop(handler, interval=CONTROL_INTERVAL):
    while True:
        handler()
        gevent.sleep(interval)


def sample_dump(queue):
    for message in queue:
        print 'MESSAGE', message


def topic(origin, *destinations):
    for message in origin:
        for destination in destinations:
            destination.put(message)


def logger_loop(log, queue):
    for message in queue:
        log(message)


def main(io):
    controller = Controller(io)

    log_file = open('session.log', 'a')
    log = Logger(json_appender(log_file))

    sample_queue = gevent.queue.Queue()
    logger_queue = gevent.queue.Queue()
    web_queue = gevent.queue.Queue()

    try:
        gevent.spawn(timer_loop, lambda: sample_queue.put(sample(io, controller)), SAMPLER_INTERVAL)
        gevent.spawn(timer_loop, controller, CONTROL_INTERVAL)
        gevent.spawn(logger_loop, log, logger_queue)
        gevent.spawn(topic, sample_queue, logger_queue, web_queue)

        webui.setup_static()
        webui.setup_controls(controller)
        webui.setup_logger(web_queue)
        run(host='0.0.0.0', port=9080, server='gevent')

    finally:
        log_file.close()

# vim:sw=4:et:ai
