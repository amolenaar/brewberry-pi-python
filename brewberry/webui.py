
import tornado.web
import tornado.httpserver
import time
from tornado.escape import json_decode

class JsonMixin(object):
    """
    Enable request handlers to prepare JSON data.
    """
    def prepare(self):
        if "application/json" in self.request.headers.get("Content-Type"):
            self.get_json = json_decode(self.request.body).get


def setup(io, sampler, mainloop):

    class HeaterHandler(JsonMixin, tornado.web.RequestHandler):
    
        def get(self):
            self.write({ 'heater': io.read_heater()})

        def post(self):
            state = self.get_json('set')
            io.set_heater('on' == state)
            self.get()


    class TemperatureHandler(JsonMixin, tornado.web.RequestHandler):
    
        def get(self):
            self.write({ 'temperature': io.read_temperature()})

        def post(self):
            t = float(self.get_json('set'))
            print 'Set temperature to', t
            # set Target temp on Controller
            self.get()


    class LoggerHandler(tornado.web.RequestHandler):

        @tornado.web.asynchronous
        def get(self):
            # TODO: add "since" parameter
            self.set_header('Content-Type', 'application/json')
            sampler.observers.add(self)

        def __call__(self, sample):
            self.write(sample.as_dict())
            self.flush()

        def on_connection_close(self):
            print 'Connection closed', id(self)
            sampler.observers.remove(self)


    application = tornado.web.Application([
        (r'/logger', LoggerHandler),
        (r'/heater', HeaterHandler),
        (r'/temperature', TemperatureHandler),
        (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
        ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9080, '0.0.0.0')

# vim:sw=4:et:ai
