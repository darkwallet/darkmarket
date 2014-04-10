import zmq
c = zmq.Context()
s = c.socket(zmq.PUSH)
s.connect("tcp://localhost:5557")
s.send("foo", flags=zmq.SNDMORE)
s.send("mykjey")

