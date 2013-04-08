
import tornado.web
import tornado.httpserver
from time import time
from tornado.escape import json_encode

import temperature

most_recent_temperature = None

def temperature_consumer(temperature):
    global most_recent_temperature
    most_recent_temperature = (temperature, time())

temperature.consumers.add(temperature_consumer)

class TemperatureHandler(tornado.web.RequestHandler):
    def get(self):
        if most_recent_temperature:
            self.write(json_encode({
                'temperature': most_recent_temperature[0],
                'timestamp': most_recent_temperature[1]
            }))
        else:
            self.set_status(204) # No data
            self.write(json_encode({'error': 'No temperature reading yet'}))

application = tornado.web.Application([
    (r"/", TemperatureHandler),
    ])

http_server = tornado.httpserver.HTTPServer(application)
def register(mainloop):
    http_server.listen(9080)

# vim:sw=4:et:ai
