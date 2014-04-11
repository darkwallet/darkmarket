import json
from protocol import reputation, query_reputation, order
from collections import defaultdict
from pyelliptic import ECC
import random

from multisig import Multisig

class Orders(object):
    def __init__(self, transport):
        self._transport = transport
        self._priv = transport._myself
        # my escrows
        self._escrows = ["02ca0020a9de236b47ca19e147cf2cd5b98b6600f168481da8ec0ca9ec92b59b76db1c3d0020f9038a585b93160632f1edec8278ddaeacc38a381c105860d702d7e81ffaa14d",
                         "02ca0020c0d9cd9bdd70c8565374ed8986ac58d24f076e9bcc401fc836352da4fc21f8490020b59dec0aff5e93184d022423893568df13ec1b8352e5f1141dbc669456af510c"]
        self._orders = {}

        transport.add_callback('order', self.on_order)


    # create a review
    def create_order(self, seller, text): # action
        id = random.randint(0,1000000)
        buyer = self._transport._myself.get_pubkey()
        new_order = order(id, buyer, seller, 'new', text, self._escrows)
        self._orders[id] = new_order
        # announce the new reputation
        self._transport.send(new_order, seller)

    def accept_order(self, new_order): # auto
        new_order['state'] = 'accepted'
        seller = new_order['seller'].decode('hex')
        buyer = new_order['buyer'].decode('hex')
        print "accept order", new_order
        new_order['escrows'] = [new_order.get('escrows')[0]]
        escrow = new_order['escrows'][0].decode('hex')
        self._multisig = Multisig(None, 2, [buyer, seller, escrow])
        new_order['address'] = self._multisig.address
        self._orders[new_order['id']] = new_order
        self._transport.send(new_order, new_order['buyer'].decode('hex'))
    
    def pay_order(self, new_order): # action
        new_order['state'] = 'payed'
        self._transport.send(new_order, new_order['seller'].decode('hex'))

    def send_order(self, new_order): # action
        new_order['state'] = 'sent'
        self._transport.send(new_order, new_order['buyer'].decode('hex'))

    def receive_order(self, new_order): # action
        new_order['state'] = 'received'
        self._transport.send(new_order, new_order['seller'].decode('hex'))

    # callbacks for messages
    # a new order has arrived
    def on_order(self, msg):
        state = msg.get('state')
        self._transport.log("Order " + state)
        buyer = msg.get('buyer').decode('hex')
        seller = msg.get('seller').decode('hex')
        myself = self._transport._myself.get_pubkey()
        if not buyer or not seller or not state:
            self._transport.log("Malformed order")
            return
        if not state == 'new' and not msg.get('id'):
            self._transport.log("Order with no id")
            return
        # check order state
        if state == 'new':
            if myself == buyer:
                self.create_order(seller, msg.get('text', 'no comments'))
            elif myself == seller:
                self.accept_order(msg)
            else:
                self._transport.log("Order not for us")
        elif state == 'accepted':
            if myself == seller:
                self._transport.log("Bad subjects [%s]" % state)
            elif myself == buyer:
                # wait for confirmation
                pass
            else:
                self._transport.log("Order not for us")
        elif state == 'payed':
            if myself == seller:
                # wait for  confirmation
                pass
            elif myself == buyer:
                self.pay_order(msg)
            else:
                self._transport.log("Order not for us")
        elif state == 'sent':
            if myself == seller:
                self.send_order(msg)
            elif myself == buyer:
                # wait for confirmation
                pass
            else:
                self._transport.log("Order not for us")
        elif state == 'received':
            if myself == seller:
                pass
                # ok
            elif myself == buyer:
                self.receive_order(msg)
            else:
                self._transport.log("Order not for us")
        if msg.get('id'):
            if msg['id'] in self._orders:
                self._orders[msg['id']]['state'] = msg['state']
            else:
                self._orders[msg['id']] = msg

if __name__ == '__main__':
    seller = ECC(curve='secp256k1')
    class FakeTransport():
        _myself = ECC(curve='secp256k1')
        def add_callback(self, section, cb):
            pass
        def send(self, msg, to=None):
            print 'sending', msg
        def log(self, msg):
            print msg
    transport = FakeTransport()
    rep = Orders(transport)
    rep.on_order(order(None, transport._myself.get_pubkey(), seller.get_pubkey(), 'new', 'One!', ["dsasd", "deadbeef"]))


