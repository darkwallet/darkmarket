import zmq
from twisted.internet import task
from twisted.internet import reactor

# Some versions of ZMQ have the error in a different module.
try:
    zmq.error
except AttributeError:
    zmq.error = zmq.core.error

class ZmqSocket:

    context = zmq.Context(1)

    def __init__(self, cb, version, type=zmq.DEALER):
        self._cb = cb
        self._type = type
        if self._type=='SUB':
            self._type = zmq.SUB

    def connect(self, address):
        self._socket = ZmqSocket.context.socket(self._type)
        self._socket.connect(address)
        if self._type==zmq.SUB:
            self._socket.setsockopt(zmq.SUBSCRIBE, '')
        l = task.LoopingCall(self.poll)
        l.start(0.1)

    def poll(self):
        try:
            data = self._socket.recv(flags=zmq.NOBLOCK)
        except zmq.error.ZMQError:
            return
        more = self._socket.getsockopt(zmq.RCVMORE)
        self._cb(data, more)

    def send(self, data, more=0):
        if more:
            more = zmq.SNDMORE
        self._socket.send(data, more)

