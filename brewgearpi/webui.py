
import tornado.web
import tornado.httpserver
from time import time
from tornado.escape import json_encode
from logger import json_appender

def setup(logger, mainloop):

    class ReadingHandler(tornado.web.RequestHandler):
        def get(self):
            last = logger.last
            if last:
                self.write(last.as_json())
            else:
                self.set_status(204) # No data
                self.flush()


    application = tornado.web.Application([
        (r'/reading', ReadingHandler),
        (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
        ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9080)

# vim:sw=4:et:ai
