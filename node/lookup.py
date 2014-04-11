import zmq

class QueryIdent:

    def __init__(self):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.REQ)
        #self._socket.connect("tcp://localhost:5558")
        self._socket.connect("tcp://85.25.195.77:5558")

    def lookup(self, user):
        self._socket.send(user)
        key = self._socket.recv()
        if key == "__NONE__":
            return None
        return key

if __name__ == "__main__":
    query = QueryIdent()
    print query.lookup("genjix").encode("hex")

