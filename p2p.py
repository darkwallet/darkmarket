import sys
import json

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
        self.send({'type': 'hello', 'uri': 'tcp://%s:12345' % MY_IP})

    def send(self, data):
        self.send_raw(json.dumps(data))

    def send_raw(self, serialized):
        self._stream.send(serialized)

    def on_message(self, msg):
        print "message received!", msg

    def closed(self, *args):
        print "peer disconnected"
 
# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, port=DEFAULT_PORT):
        self._peers = {}
        self._port = port

    def join_network(self):
        self.listen()
        if SEED_URI:
            self.init_peer(SEED_URI)

    def listen(self):
        print "init server"
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REP)
        self._socket.bind('tcp://'+MY_IP+':%s' % self._port)
        self._stream = zmqstream.ZMQStream(self._socket)
        self._stream.on_recv(self.on_message)

    def init_peer(self, uri):
        print "init peer", uri
        if not uri in self._peers:
            self._peers[uri] = PeerConnection(uri)

    def send(self, data):
        print " * sending", data
        serialized = json.dumps(data)
        for peer in self._peers.keys():
            try:
                peer.send_raw(serialized)
            except:
                print "error sending over peer!"

    def on_opening(self, uri):
        self.init_peer(uri)

    def on_message(self, serialized):
        try:
            msg = json.loads(serialized[0])
        except:
            print "incorrect msg!", serialized
            return

        msg_type = msg.get('type')
        if msg_type == 'hello' and msg.get('uri'):
            self.on_opening(msg.get('uri'))


