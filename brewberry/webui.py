
import tornado.web
import tornado.httpserver
import time
from tornado.escape import json_encode
from logger import json_appender

def setup(sampler, mainloop):

    class LoggerHandler(tornado.web.RequestHandler):
        # TODO: add "since" parameter
        @tornado.web.asynchronous
        def get(self):
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
        (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
        ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9080, '0.0.0.0')

# vim:sw=4:et:ai
