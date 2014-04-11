import json
import pyelliptic as ec

from p2p import PeerConnection, TransportLayer
from multiprocessing import Process
import traceback

from protocol import hello

class CryptoPeerConnection(PeerConnection):
    def __init__(self, address, transport, pub):
        self._transport = transport
        self._priv = transport._myself
        self._pub = pub
        PeerConnection.__init__(self, address)

    def encrypt(self, data):
        return self._priv.encrypt(data, self._pub)

    def send(self, data):
        self.send_raw(self.encrypt(json.dumps(data)))

    def on_message(self, msg):
        # this are just acks
        pass


class CryptoTransportLayer(TransportLayer):
    def __init__(self, port=None):
        TransportLayer.__init__(self, port)
        self._myself = ec.ECC(curve='secp256k1')

    def get_profile(self):
        peers = {}
        for uri, peer in self._peers.iteritems():
            if peer._pub:
                peers[uri] = peer._pub.encode('hex')
        return {'uri': self._uri, 'pub': self._myself.get_pubkey().encode('hex'), 'peers': peers}

    def create_peer(self, uri, pub):
        if pub:
            self.log("init peer " + uri + " " + pub[0:8], '*')
            pub = pub.decode('hex')
        else:
            self.log("init peer [seed] " + uri, '*')

        # create the peer
        self._peers[uri] = CryptoPeerConnection(uri, self, pub)

        # call 'peer' callbacks on listeners
        self.trigger_callbacks('peer', self._peers[uri])

        # now send a hello message to the peer
        if pub:
            self.log("sending encrypted profile to %s" % uri)
            self._peers[uri].send(hello(self.get_profile()))
        else:
            # this is needed for the first connection
            self.log("sending  normal profile to %s" % uri)
            profile = hello(self.get_profile())
            self._peers[uri].send_raw(json.dumps(profile))

    def init_peer(self, msg):
        uri = msg['uri']
        pub = msg.get('pub')
        if not uri in self._peers:
            self.create_peer(uri, pub)
        elif pub and not self._peers[uri]._pub:
            self.log("setting pub for seed node")
            self._peers[uri]._pub = pub.decode('hex')

    def on_raw_message(self, serialized):
        try:
            msg = json.loads(serialized)
            self.log("receive [%s]" % msg.get('type', 'unknown'))
        except ValueError:
            try:
                msg = json.loads(self._myself.decrypt(serialized))
                self.log("decrypted [%s]" % msg.get('type', 'unknown'))
            except:
                self.log("incorrect msg ! %s..." % self._myself.decrypt(serialized))
                traceback.print_exc()
                return

        msg_type = msg.get('type')
        if msg_type == 'hello' and msg.get('uri'):
            self.init_peer(msg)
            for uri, pub in msg.get('peers', {}).iteritems():
                self.init_peer({'uri': uri, 'pub': pub})
            self.log("Update peer table [%s peers]" % len(self._peers))
        else:
            self.on_message(msg)


