import json
from protocol import reputation, query_reputation
from collections import defaultdict
from pyelliptic import ECC

def review(pubkey, subject, signature, text, rating):
    data = {}
    # this is who signs
    data['pubkey'] = pubkey.encode('hex')
    # this is who the review is about
    data['subject'] = subject.encode('hex')
    # the signature
    data['sig'] = signature.encode('hex')
    # some text
    data['text'] = text
    # rating
    data['rating'] = rating
    return data

class Reputation(object):
    def __init__(self, transport):
        self._transport = transport
        self._priv = transport._myself
        self._reviews = defaultdict(list)

        transport.add_callback('reputation', self.on_reputation)
        transport.add_callback('query_reputation', self.on_query_reputation)

        # Of course :-)
        self.create_review(self._priv.get_pubkey(), "Best shop ever", 10)

    # getting reputation from inside the application
    def get_reputation(self, pubkey):
        return self._reviews[pubkey]

    def get_my_reputation(self):
        return self._reviews[self._priv.get_pubkey()]

    # create a review
    def create_review(self, pubkey, text, rating):
        signature = self._priv.sign(self._build_review(pubkey, text, rating))
        new_review = review(self._priv.get_pubkey(), pubkey, signature, text, rating)
        self._reviews[pubkey].append(new_review)
        # announce the new reputation
        self._transport.send(reputation(pubkey, [new_review]))

    # what we sign
    def _build_review(self, pubkey, text, rating):
        return json.dumps([pubkey.encode('hex'),  text, rating])

    def query_reputation(self, pubkey):
        self._transport.send(query_reputation(pubkey))

    def parse_review(self, msg):
        pubkey = msg['pubkey'].decode('hex')
        subject = msg['subject'].decode('hex')
        signature = msg['sig'].decode('hex')
        text = msg['text']
        rating = msg['rating']

        # check the signature
        valid = ECC(pubkey=pubkey).verify(signature, self._build_review(subject, str(text), rating))
        
        if valid:
            newreview = review(pubkey, subject, signature, text, rating)
            self._reviews[pubkey].append(newreview)
        else:
            self._transport.log("[reputation] Invalid review!")


    # callbacks for messages
    # a new review has arrived
    def on_reputation(self, msg):
        for review in msg.get('reviews', []):
            self.parse_review(review)

    # query reviews has arrived
    def on_query_reputation(self, msg):
        pubkey = msg['pubkey'].decode('hex')
        if pubkey in self._reviews:
            self._transport.send(reputation(pubkey, self._reviews[pubkey]))


if __name__ == '__main__':
    class FakeTransport():
        _myself = ECC(curve='secp256k1')
        def add_callback(self, section, cb):
            pass
        def send(self, msg):
            print 'sending', msg
        def log(self, msg):
            print msg
    transport = FakeTransport()
    rep = Reputation(transport)
    print rep.get_reputation(transport._myself.get_pubkey())
    print rep.get_my_reputation()
