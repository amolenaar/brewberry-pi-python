
import tornado.web
import tornado.httpserver
from time import time
from tornado.escape import json_encode


def setup(io, mainloop):

    class ReadingHandler(tornado.web.RequestHandler):
        def get(self):
            self.write({
                'time': io.read_time(),
                'temperature': io.read_temperature(),
                'heater': io.read_heater()
            })

    application = tornado.web.Application([
        (r'/reading', ReadingHandler),
        (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
        ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9080)

# vim:sw=4:et:ai
