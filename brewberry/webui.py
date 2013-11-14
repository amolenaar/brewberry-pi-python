
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
            self.set_header('Content-Type', 'application/json')
            sampler.observers.add(self)

        def __call__(self, sample):
            self.write(sample.as_dict())
            self.flush()
            #sampler.observers.remove(self)

        def on_connection_close(self):
            print 'Connection closed', id(self)
            sampler.observers.remove(self)

    class HistoryHandler(tornado.web.RequestHandler):

        def get(self):
            since = self.get_argument('since')
            # TODO: assert: matches: \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d
            with open('session.log') as f:
                samples = []
                for line in f:
                    sample = json_decode(line)
                    # String compare is sufficient
                    if sample['time'] > since:
                        samples.append(sample)
            self.write(json_encode(samples))

    application = tornado.web.Application([
        (r'/logger/feed', LoggerHandler),
        (r'/logger/history', HistoryHandler),
        (r'/controller', ControllerHandler),
        (r'/temperature', TemperatureHandler),
        (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
        ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9080, '0.0.0.0')

# vim:sw=4:et:ai
