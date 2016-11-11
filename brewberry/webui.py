
from gevent.queue import Queue
from bottle import get, post, request, response, static_file, redirect
import json

def setup_static():

    @get('/<filename:re:.*\.(html|css|js)>')
    def server_static(filename):
        return static_file(filename, root='./static')

    @get('/')
    def root():
        return redirect('index.html')


def setup_controls(controller):

    @get("/controller")
    def get_controller_state():
        return { 'controller': controller.started }

    @post("/controller")
    def set_controller_state():
        state = request.json['set']
        controller(start=('on' == state))

    @get("/temperature")
    def get_temperature():
        return { 'mash-temperature': controller.mash_temperature }

    @post("/temperature")
    def set_temperature():
        t = float(request.json['set'])
        controller(temperature=t)

def setup_logger(topic_registry):
    @get('/logger')
    def logger():
        # "Using server-sent events"
        # https://developer.mozilla.org/en-US/docs/Server-sent_events/Using_server-sent_events
        # "Stream updates with server-sent events"
        # http://www.html5rocks.com/en/tutorials/eventsource/basics/

        response.content_type  = 'text/event-stream'
        response.cache_control = 'no-cache'

        # Set client-side auto-reconnect timeout, ms.
        yield 'retry: 100\n\n'

        queue = Queue()
        queue_put = queue.put
        try:
            topic_registry(register=queue_put)
            # TODO: need one queue per listener
            for sample in queue:
                s = sample.as_dict()
                yield 'id: %s\nevent: sample\ndata: %s\n\n' % (s['time'], json.dumps(s))
        finally:
            topic_registry(deregister=queue_put)

# vim:sw=4:et:ai
