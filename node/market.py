from protocol import shout
from reputation import Reputation

class Market(object):
    def __init__(self, transport):
        transport.log("[market] Initializing")

        # for now we have the id in the transport
        self._myself = transport._myself
        self._peers = transport._peers
        self._transport = transport

        self.reputation = Reputation(self._transport)


        # if something comes in, store it:
        self.nicks = []
        self.reps = []
        self.pages = []

        # register callbacks for incoming events
        transport.add_callback('message', self.on_message)
        transport.add_callback('peer', self.on_peer)

        # send something
        transport.send(shout({'subject': 'xxxxx'}))

    def on_peer(self, peer):
        self._transport.log("[market] new peer")

    def on_message(self, msg):
        self._transport.log("[market] generic message")
        msg_type = msg.get('type')
        if msg_type == 'get_page' and msg.get('who'):
            print "got page request:"
            print msg.get('who')
            # TODO: if who is us, reply with our seller page

        if msg_type == 'page' and msg.get('who') and msg.get('content'):
            print "got page:"
            print msg.get('who')
            print msg.get('content')
            # TODO: store the content in the pages array

    def send_page(self, who, content):
        self._transport.send({'type': 'page', 'who': who, 'content': content})

    def send_get_page(self, who):
        self._transport.send(shout({'subject': 'xxxxx'}))
        #self._transport.send({'type': 'get-page', 'who': who})
