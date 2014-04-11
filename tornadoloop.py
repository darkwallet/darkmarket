import sys
import json

import tornado.ioloop
import tornado.web
from zmq.eventloop import ioloop, zmqstream
import zmq
ioloop.install()

from crypto2crypto import CryptoTransportLayer


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class MarketApplication(tornado.web.Application):
 
    def __init__(self):
        settings = dict(debug=True)
        handlers = [
            (r"/foo", MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        self.transport = CryptoTransportLayer(12345)
        self.transport.join_network()


if __name__ == "__main__":
    application = MarketApplication()
    error = True
    port = 8888
    while error and port < 8988:
        try:
            application.listen(port)
            error = False
        except:
            port += 1
    print " - started user port on %s" % port
    tornado.ioloop.IOLoop.instance().start()

