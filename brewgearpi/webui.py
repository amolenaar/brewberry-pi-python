
import tornado.web
import tornado.httpserver
from time import time
from tornado.escape import json_encode

most_recent_temperature = [0, 0]

class TemperatureHandler(tornado.web.RequestHandler):
    def get(self):
        if most_recent_temperature:
            self.write({
                'temperature': most_recent_temperature[0],
                'timestamp': most_recent_temperature[1]
            })
        else:
            self.set_status(204) # No data
            self.flush()


application = tornado.web.Application([
    (r'/temperature', TemperatureHandler),
    (r'/(..*)', tornado.web.StaticFileHandler, {'path': 'static'}),
    (r'/$', tornado.web.RedirectHandler, {"url": "/index.html"})
    ])

http_server = tornado.httpserver.HTTPServer(application)
def register(mainloop):
    http_server.listen(9080)

# vim:sw=4:et:ai
