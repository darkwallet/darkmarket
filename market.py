from protocol import shout

class Market(object):
    def __init__(self, transport):
        transport.log("[market] Initializing")

        # for now we have the id in the transport
        self._myself = transport._myself
        self._peers = transport._myself
        self._transport = transport

        # register callbacks for incoming events
        transport.add_callback('message', self.on_message)
        transport.add_callback('peer', self.on_peer)

        # send something
        transport.send(shout({'subject': 'xxxxx'}))

    def on_peer(self, peer):
        self._transport.log("[market] new peer")

    def on_message(self, msg):
        self._transport.log("[market] generic message")
