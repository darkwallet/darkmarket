import sys
import json
from collections import defaultdict

import pyelliptic as ec

from zmq.eventloop import ioloop, zmqstream
import zmq
from multiprocessing import Process
from threading import Thread
ioloop.install()
import traceback

# Default port
DEFAULT_PORT=12345

# Get some command line pars
SEED_URI = False
if len(sys.argv) > 1:
    MY_IP = sys.argv[1]
else:
    MY_IP = "127.0.0.1"
if len(sys.argv) > 2:
    SEED_URI = sys.argv[2] # like tcp://127.0.0.1:12345
else:
    print "warning no seed!! you should call like [market myip seeduri]"

# Connection to one peer
class PeerConnection(object):
    def __init__(self, address):
        self._address = address

    def create_socket(self):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REQ)
        self._socket.connect(self._address)

    def cleanup_socket(self):
        self._socket.close()

    def send(self, data):
        self.send_raw(json.dumps(data))

    def send_raw(self, serialized):
        Process(target=self._send_raw, args=(serialized,)).start()

    def _send_raw(self, serialized):
        self.create_socket()

        self._socket.send(serialized)
        msg = self._socket.recv()
        self.on_message(msg)

        self.cleanup_socket()

    def on_message(self, msg):
        print "message received!", msg

    def closed(self, *args):
        print " - peer disconnected"

# Transport layer manages a list of peers
class TransportLayer(object):
    def __init__(self, port=DEFAULT_PORT):
        self._peers = {}
        self._callbacks = defaultdict(list)
        self._id = MY_IP[-1] # hack for logging
        self._port = port
        self._uri = 'tcp://%s:%s' % (MY_IP, self._port)

    def add_callback(self, section, callback):
        self._callbacks[section].append(callback)

    def trigger_callbacks(self, section, *data):
        for cb in self._callbacks[section]:
            cb(*data)
        if not section == 'all':
            for cb in self._callbacks['all']:
                cb(*data)

    def get_profile(self):
        return {'type': 'hello', 'uri': 'tcp://%s:12345' % MY_IP}

    def join_network(self):
        self.listen()
        if SEED_URI:
            self.init_peer({'uri': SEED_URI})

    def listen(self):
        Thread(target=self._listen).start()

    def _listen(self):
        self.log("init server %s %s" % (MY_IP, self._port))
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REP)
        self._socket.bind(self._uri)
        while True:
            message = self._socket.recv()
            self.on_raw_message(message)
            self._socket.send(json.dumps({'type': "ok"}))

    def closed(self, *args):
        print "client left"

    def init_peer(self, msg):
        uri = msg['uri']
        self.log("init peer %s" %  msg)
        if not uri in self._peers:
            self._peers[uri] = PeerConnection(uri)

    def log(self, msg, pointer='-'):
        print " %s [%s] %s" % (pointer, self._id, msg)

    def send(self, data):
        self.log("sending %s..." % data.keys())
        for peer in self._peers.values():
            try:
                if peer._pub:
                    peer.send(data)
                else:
                    serialized = json.dumps(data)
                    peer.send_raw(serialized)
            except:
                print "error sending over peer!"
                traceback.print_exc()

    def on_message(self, msg):
        # here goes the application callbacks
        # we get a "clean" msg which is a dict holding whatever
        self.trigger_callbacks(msg.get('type'), msg)

    def on_raw_message(self, serialized):
        self.log("connected " +str(len(serialized)))
        try:
            msg = json.loads(serialized[0])
        except:
            self.log("incorrect msg! " + serialized)
            return

        msg_type = msg.get('type')
        if msg_type == 'hello' and msg.get('uri'):
            self.init_peer(msg)
        else:
            self.on_message(msg)

