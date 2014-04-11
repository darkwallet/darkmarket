import zmq
c = zmq.Context()
s = c.socket(zmq.PUSH)
s.connect("tcp://localhost:5557")
# secret = 45c18922a7c2fe9997335fd1758acf2c6ba6a30f76d085c9a9ccabd84fe5efeb
#s.send("novaprospekt", flags=zmq.SNDMORE)
#s.send("03f881d01573c94ce7a92132479c612448140330aadbfad447543319d95af4ccc7".decode("hex"))
# secret = b52bafc3498e5b8b594b9737ec74e4bec181c8422cb4cb6b7de81da2a9463a2a
#s.send("s_tec", flags=zmq.SNDMORE)
#s.send("02f5127844ffad50431ff9b9866c7506d7b2128e136207eb4efb89ce23ad01c0d4".decode("hex"))
## secret = 393baa997f92684ab6edde18af59f99e0d0cda07b09e6a4390aa09bb50fe7eb8
#s.send("genjix", flags=zmq.SNDMORE)
#s.send("03dfef47115e6d43d45eddbc9ee4491cc176b4821fcf9cb5c99bcd7bef0bfbea24".decode("hex"))
## secret = 4196a69555f599b75744029867f39a36258090f79dc616541e174d3f72ff50c2
s.send("caedes", flags=zmq.SNDMORE)
s.send("03960478444a2c18b0cd82b461c2654fc3b96dd117ddd524558268be3044192b97".decode("hex"))

