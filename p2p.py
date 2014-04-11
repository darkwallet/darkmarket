import sys
import json

import pyelliptic as ec

from zmq.eventloop import ioloop, zmqstream
import zmq
ioloop.install()

# Default port
DEFAULT_PORT=12345

# Get some command line pars
SEED_URI = False
MY_IP = sys.argv[1]
if len(sys.argv) > 2:
    SEED_URI = sys.argv[2] # like tcp://127.0.0.1:12345
else:
    print "warning no seed!! you should call like [market myip seeduri]"

# Connection to one peer
class PeerConnection(object):
    def __init__(self, address):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REQ)
        self._socket.connect(address)
        self._stream = zmqstream.ZMQStream(self._socket)
        self._stream.on_recv(self.on_message)
        self._stream.set_close_callback(self.closed)

    def send(self, data):
        self.send_raw(json.dumps(data))

    def send_raw(self, serialized):
        self._stream.send(serialized)

    def on_message(self, msg):
        print "message received!", msg

    def closed(self, *args):
        print " - peer disconnected"
 
# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, port=DEFAULT_PORT):
        self._peers = {}
        self._port = port
        self._uri = 'tcp://%s:%s' % (MY_IP, self._port)
        self._id = MY_IP[-1] # hack for logging

    def get_profile(self):
        return {'type': 'hello', 'uri': 'tcp://%s:12345' % MY_IP}

    def join_network(self):
        self.listen()
        if SEED_URI:
            self.init_peer({'uri': SEED_URI})
            self.send(self.get_profile())

    def listen(self):
        self.log("init server %s %s" % (MY_IP, self._port))
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.XREP)
        self._socket.bind(self._uri)
        self._stream = zmqstream.ZMQStream(self._socket)
        self._stream.on_recv(self.on_raw_message)

    def init_peer(self, msg):
        uri = msg['uri']
        self.log("init peer %s" %  msg)
        if not uri in self._peers:
            self._peers[uri] = PeerConnection(uri)

    def log(self, msg, pointer='-'):
        print " %s [%s] %s" % (pointer, self._id, msg)

    def send(self, data):
        self.log("sending %s" % data)
        serialized = json.dumps(data)
        for peer in self._peers.values():
            try:
                peer.send_raw(serialized)
            except:
                print "error sending over peer!"

    def on_raw_message(self, serialized):
        self.log("connected")
        try:
            msg = json.loads(serialized[0])
        except:
            self.log("incorrect msg! " + serialized)
            return

        msg_type = msg.get('type')
        if msg_type == 'hello' and msg.get('uri'):
            self.init_peer(msg)


