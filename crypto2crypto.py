import json
import pyelliptic as ec

from p2p import PeerConnection, TransportLayer
import traceback

class CryptoPeerConnection(PeerConnection):
    def __init__(self, address, transport, pub):
        self._transport = transport
        self._priv = transport._myself
        self._pub = pub
        PeerConnection.__init__(self, address)

    def encrypt(self, data):
        return self._priv.encrypt(data, self._pub)

    def send(self, data):
        self._transport.log("send", data['type'])
        self.send_raw(self.encrypt(json.dumps(data)))

    def send_raw(self, serialized):
        self._stream.send(serialized)

    def on_message(self, msg):
        self.transport.on_raw_message(msg)



class CryptoTransportLayer(TransportLayer):
    def __init__(self, port=None):
        TransportLayer.__init__(self, port)
        self._myself = ec.ECC(curve='secp256k1')

    def get_profile(self):
        peers = {}
        for uri, peer in self._peers.iteritems():
            if peer._pub:
                peers[uri] = peer._pub.encode('hex')
        return {'type': 'hello', 'uri': self._uri, 'pub': self._myself.get_pubkey().encode('hex'), 'peers': peers}

    def init_peer(self, msg):
        uri = msg['uri']
        pub = msg.get('pub')
        if not uri in self._peers:
            if pub:
                self.log("init crypto peer " + uri + " " + pub[0:8])
                pub = pub.decode('hex')
            else:
                self.log("init seed peer " + uri)
            self._peers[uri] = CryptoPeerConnection(uri, self, pub)
            if pub:
                self._peers[uri].send(self.get_profile())
            else:
                # this is needed for the first connection
                self._peers[uri].send_raw(json.dumps(self.get_profile()))
        elif pub and not self._peers[uri]._pub:
            self.log("setting pub for seed node")
            self._peers[uri]._pub = pub


    def on_raw_message(self, serialized):
        self.log("receive")
        try:
            msg = json.loads(serialized[0])
            self.log("receive " + msg['type'])
        except:
            try:
                msg = self._myself.decrypt(serialized)
                msg = json.loads(msg)
                self.log("decrypted " + msg.get('type', 'unknown'))
            except:
                self.log("incorrect msg ! %s..." % serialized[0][:8])
                # traceback.print_exc()
                return

        msg_type = msg.get('type')
        if msg_type == 'hello' and msg.get('uri'):
            self.init_peer(msg)
            print msg.get('peers')
        else:
            self.on_message(msg)


