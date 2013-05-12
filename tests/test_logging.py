

from brewgearpi import logger
from StringIO import StringIO
import datetime

def test_json_output():
    log_line = logger.LogLine(datetime.datetime.utcfromtimestamp(0), 20.0, Off)
    io = StringIO()
    tojson = logger.json_appender(io)
    tojson(log_line)
    assert io.getvalue() == '{"heater": 0, "temperature": 20.0, "time": "1970-01-01T00:00:00"}\n', '"%s"' % io.getvalue()

# vim:sw=4:et:ai
