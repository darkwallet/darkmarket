import tornado.websocket
import threading
import logging

class ProtocolHandler:
    def __init__(self):
        self._handlers = {
            "query_seller":  ObJsonChanPost,
            "test":          ObJsonChanList,
        }

    def handle_request(self, socket_handler, request):
        command = request["command"]
        if command not in self._handlers:
            return False
        params = request["params"]
        # Create callback handler to write response to the socket.
        handler = self._handlers[command](socket_handler, request["id"], self._json_chan, self)
        try:
            params = handler.translate_arguments(params)
        except Exception as exc:
            logging.error("Bad parameters specified: %s", exc, exc_info=True)
            return True
        try:
            handler.process(params)
        except Exception as e:
            handler.process_response(str(e), {})
        return True



class WebSocketHandler(tornado.websocket.WebSocketHandler):

    # Set of WebsocketHandler
    listeners = set()
    # Protects listeners
    listen_lock = threading.Lock()

    def initialize(self, node):
        self._app_handler = self #self.application.protocol_handler
        self.node = node

    def handle_request(self, *args):
        print "request", args

    def open(self):
        print "open"
        with WebSocketHandler.listen_lock:
            self.listeners.add(self)
        self._connected = True

    def on_close(self):
        print "close"
        disconnect_msg = {'command': 'disconnect_client', 'id': 0, 'params': []}
        self._connected = False
        self._app_handler.handle_request(self, disconnect_msg)
        with WebSocketHandler.listen_lock:
            self.listeners.remove(self)

    def _check_request(self, request):
        return request.has_key("command") and request.has_key("id") and \
            request.has_key("params") and type(request["params"]) == list

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
