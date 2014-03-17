
import tornado.web
import tornado.httpserver
import time
from tornado.escape import json_encode, json_decode

class JsonMixin(object):
    """
    Enable request handlers to prepare JSON data.
    """
    def prepare(self):
        if "application/json" in self.request.headers.get("Content-Type"):
            self.get_json = json_decode(self.request.body).get

def setup(io, sampler, controller, mainloop):

    # TODO: put temp. dialog on top of screen instead of dialog in the middle.
    # Deprecated, should start/stop mash process, works on controller
    class ControllerHandler(JsonMixin, tornado.web.RequestHandler):
    
        def get(self):
            self.write({ 'controller': controller.started })

        def post(self):
            state = self.get_json('set')
            controller.started = ('on' == state)
            self.get()


    class TemperatureHandler(JsonMixin, tornado.web.RequestHandler):
    
        def get(self):
            self.write({ 'mash-temperature': controller.mash_temperature })

        def post(self):
            t = float(self.get_json('set'))
            print 'Set temperature to', t
            # set Target temp on Controller
            controller.mash_temperature = t
            self.get()


    class LoggerHandler(tornado.web.RequestHandler):

        @tornado.web.asynchronous
        def get(self):
            if not 'text/event-stream' in self.request.headers.get("Accept"):
                self.write('Expected an event stream')
                self.flush()
                self.finish()
                return
            self.set_header('Content-Type', 'text/event-stream')
            self.set_header('Cache-Control', 'no-cache, no-store')
            last_event_id = self.request.headers.get('Last-Event-ID')
            print 'last event: ', last_event_id
            if last_event_id:
                self.send_old_samples(last_event_id)
            # TODO: send out events since last_event_id
            sampler.observers.add(self)

        def __call__(self, sample):
            s = sample.as_dict()
            self.write('id: %s\n' % s['time'])
            self.write('event: sample\n')
            self.write('data: %s\n\n' % json_encode(s))
            self.flush()

        def on_connection_close(self):
            print 'Connection closed', id(self)
            sampler.observers.remove(self)

        def send_old_samples(self, since):
            # TODO: assert: matches: \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d
            with open('session.log') as f:
                samples = []
                for line in f:
                    sample = json_decode(line)
                    # String compare is sufficient
                    if sample['time'] > since:
                        self.write('id: %s\n' % sample['time'])
                        self.write('event: sample\n')
                        self.write('data: %s\n\n' % line)
                        self.flush()

    application = tornado.web.Application([
        (r'/logger', LoggerHandler),
        (r'/controller', ControllerHandler),
        (r'/temperature', TemperatureHandler),
        (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
        ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9080, '0.0.0.0')

# vim:sw=4:et:ai
