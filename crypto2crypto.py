import json
import pyelliptic as ec

from p2p import PeerConnection, TransportLayer


class CryptoPeerConnection(PeerConnection):
    def __init__(self, address, myself, pub):
        self._priv = myself
        self._pub = pub
        PeerConnection.__init__(self, address)

    def on_message(self, msg):
        print "message received!", msg

    def encrypt(self, data):
        if self._pub:
            return self._priv.encrypt(data, self._pub)
        else:
            return data

    def send(self, data):
        print "send", data
        self.send_raw(self.encrypt(json.dumps(data)))

    def send_raw(self, serialized):
        self._stream.send(serialized)

    def on_message(self, msg):
        print "message received!", msg



class CryptoTransportLayer(TransportLayer):
    def __init__(self, port=None):
        TransportLayer.__init__(self, port)
        self._myself = ec.ECC(curve='secp256k1')

    def get_profile(self):
        return {'type': 'hello', 'uri': self._uri, 'pub': self._myself.get_pubkey().encode('hex')}

    def init_peer(self, msg):
        uri = msg['uri']
        pub = msg.get('pub')
        print "init crypto peer", uri, pub
        if not uri in self._peers:
            if pub:
                pub = pub.decode('hex')
            self._peers[uri] = CryptoPeerConnection(uri, self._myself, pub)
            self._peers[uri].send(self.get_profile())


    def on_message(self, serialized):
        print "connected"
        try:
            msg = json.loads(serialized[0])
        except:
            try:
                msg = self._priv.decrypt(serialized[0])
                msg = json.loads(msg)
            except:
                print "incorrect msg!", serialized
                return

        msg_type = msg.get('type')
        if msg_type == 'hello' and msg.get('uri'):
            self.init_peer(msg)


