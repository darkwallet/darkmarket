from protocol import shout, page, query_page
from reputation import Reputation
from orders import Orders


class Market(object):
    def __init__(self, transport):
        transport.log("[market] Initializing")

        # for now we have the id in the transport
        self._myself = transport._myself
        self._peers = transport._peers
        self._transport = transport

        self.reputation = Reputation(self._transport)
        self.orders = Orders(self._transport)


        # if something comes in, store it:
        self.nicks = {}
        self.pages = {}

        # register callbacks for incoming events
        transport.add_callback('peer', self.on_peer)
        transport.add_callback('query_page', self.on_query_page)
        transport.add_callback('page', self.on_page)
        transport.add_callback('negotiate_pubkey', self.on_negotiate_pubkey)
        transport.add_callback('response_pubkey', self.on_response_pubkey)

        self.load_page()

        # send something
        transport.send(shout({'text': 'xxxxx'}))

    def load_page(self):
        f = open('shop/myshop.txt')
        data = f.read()
        f.close()
        self.mypage = data
        self.signature = self._transport._myself.sign(data)

    def query_page(self, pubkey):
        self._transport.send(query_page(pubkey))

    def on_page(self, page):
        self._transport.log("[market] got page " + str(page))
        pubkey = page.get('pubkey')
        page = page.get('text')
        if pubkey and page:
            self.pages[pubkey] = page
        

    def on_query_page(self, peer):
        self._transport.log("[market] query page " + str(peer))
        self._transport.send(page(self._transport._myself.get_pubkey(), self.mypage, self.signature))

    def on_peer(self, peer):
        self._transport.log("[market] new peer")

    def on_negotiate_pubkey(self, ident_pubkey):
        self._transport.log("[market] asking my real pubkey")
        assert "nickname" in ident_pubkey
        assert "ident_pubkey" in ident_pubkey
        nickname = ident_pubkey['nickname']
        ident_pubkey = ident_pubkey['ident_pubkey'].decode("hex")
        self._transport.respond_pubkey_if_mine(nickname, ident_pubkey)

    def on_response_pubkey(self, response):
        self._transport.log("[market] got a pubkey!")
        assert "pubkey" in response
        assert "nickname" in response
        assert "signature" in response
        pubkey = response["pubkey"].decode("hex")
        signature = response["signature"].decode("hex")
        nickname = response["nickname"]
        # Cache mapping for later.
        if not self._transport.nick_mapping.has_key(nickname):
            self._transport.nick_mapping[nickname] = [None, pubkey]
        # Verify signature here...
        # Add to our dict.
        self._transport.nick_mapping[nickname][1] = pubkey
        self._transport.log("[market] mappings: ###############")
        for k, v in self._transport.nick_mapping.iteritems():
            self._transport.log("'%s' -> '%s' (%s)" % (
                k, v[1].encode("hex") if v[1] is not None else v[1],
                v[0].encode("hex") if v[0] is not None else v[0]))
        self._transport.log("##################################")

