import tornado.websocket
import threading
import logging
import json
import tornado.ioloop
import random
import protocol
import lookup

class ProtocolHandler:
    def __init__(self, transport, node, handler):
        self.node = node
        self._transport = transport
        self._handler = handler

        # register on transport events to forward..
        transport.add_callback('peer', self.on_node_peer)
        transport.add_callback('page', self.on_node_page)
        transport.add_callback('all', self.on_node_message)

        # handlers from events coming from websocket, we shouldnt need this
        self._handlers = {
            "query_page":          self.client_query_page,
            "review":          self.client_review,
            "search":          self.client_search,
            "shout":          self.client_shout
        }

        self.query_ident = None

    def send_opening(self):
        peers = []
        for uri, peer in self._transport._peers.items():
            peer_item = {'uri': uri}
            if peer._pub:
               peer_item['pubkey'] = peer._pub.encode('hex')
            else:
               peer_item['pubkey'] = 'unknown'
            peers.append(peer_item)
        message = {
            'type': 'myself',
            'pubkey': self._transport._myself.get_pubkey().encode('hex'),
            'peers': peers,
            'reputation': self.node.reputation.get_my_reputation()
        }
        self.send_to_client(None, message)

    # requests coming from the client
    def client_query_page(self, socket_handler, msg):
        pubkey = msg['pubkey'].decode('hex')
        self.node.query_page(pubkey)
        self.node.reputation.query_reputation(pubkey)

    def client_review(self, socket_handler, msg):
        pubkey = msg['pubkey'].decode('hex')
        text = msg['text']
        rating = msg['rating']
        self.node.reputation.create_review(pubkey, text, rating)

    def client_search(self, socket_handler, msg):
        print "begin"
        if self.query_ident is None:
            print "Initializing"
            self.query_ident = lookup.QueryIdent()
        print "search", msg
        #key = self.query_ident.lookup(str(msg["text"]))
        key = "hello"
        print "Done."
        if key is None:
            print "Key not found!"
            return
        print "key", key.encode("hex")

    def client_shout(self, socket_handler, msg):
        self._transport.send(protocol.shout(msg))

    # messages coming from "the market"
    def on_node_peer(self, peer):
        response = {'type': 'peer', 'pubkey': peer._pub.encode('hex'), 'uri': peer._address}
        self.send_to_client(None, response)

    def on_node_page(self, page):
        self.send_to_client(None, page)

    def on_node_message(self, *args):
        first = args[0]
        if isinstance(first, dict):
            self.send_to_client(None, first)
        else:
            self._transport.log("can't format")

    # send a message
    def send_to_client(self, error, result):
        assert error is None or type(error) == str
        response = {
            "id": random.randint(0, 1000000),
            "result": result
        }
        if error:
            response["error"] = error
        self._handler.queue_response(response)

    # handler a request
    def handle_request(self, socket_handler, request):
        command = request["command"]
        if command not in self._handlers:
            return False
        params = request["params"]
        # Create callback handler to write response to the socket.
        handler = self._handlers[command](socket_handler, params)
        return True


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    # Set of WebsocketHandler
    listeners = set()
    # Protects listeners
    listen_lock = threading.Lock()

    def initialize(self, transport, node):
        transport.log("initialize websockethandler")
        self._app_handler = ProtocolHandler(transport, node, self)
        self.node = node
        self._transport = transport

    def open(self):
        self._transport.log("websocket open")
        self._app_handler.send_opening()
        with WebSocketHandler.listen_lock:
            self.listeners.add(self)
        self._connected = True

    def on_close(self):
        self._transport.log("websocket closed")
        disconnect_msg = {'command': 'disconnect_client', 'id': 0, 'params': []}
        self._connected = False
        self._app_handler.handle_request(self, disconnect_msg)
        with WebSocketHandler.listen_lock:
            self.listeners.remove(self)

    def _check_request(self, request):
        return request.has_key("command") and request.has_key("id") and \
            request.has_key("params") and type(request["params"]) == dict
            #request.has_key("params") and type(request["params"]) == list

    def on_message(self, message):
        try:
            request = json.loads(message)
        except:
            logging.error("Error decoding message: %s", message, exc_info=True)

        # Check request is correctly formed.
        if not self._check_request(request):
            logging.error("Malformed request: %s", request, exc_info=True)
            return
        if self._app_handler.handle_request(self, request):
            return

    def _send_response(self, response):
        if self.ws_connection:
            self.write_message(json.dumps(response))
        #try:
        #    self.write_message(json.dumps(response))
        #except tornado.websocket.WebSocketClosedError:
        #    logging.warning("Dropping response to closed socket: %s",
        #       response, exc_info=True)

    def queue_response(self, response):
        ioloop = tornado.ioloop.IOLoop.instance()
        def send_response(*args):
            self._send_response(response)
        try:
            # calling write_message or the socket is not thread safe
            ioloop.add_callback(send_response)
        except:
            logging.error("Error adding callback", exc_info=True)

