function Connection(onMessage) {

  socket_uri = document.URL.replace(/https?:(.*)\/html\/.*/, "ws:$1/ws");
  var websocket = new WebSocket(socket_uri);

  websocket.onopen = function(evt) {
   console.log("open!", evt)
  }

  websocket.onclose = function(evt) {
   console.log("closed", evt)
  }

  websocket.onerror = function(evt) {
   console.log("error", evt)
  }

  websocket.onmessage = function(evt) {
   var data = JSON.parse(evt.data)
   console.log("message", data.result)
   onMessage(data.result)
  }
  this.websocket = websocket;
  var self = this;

  this.send = function(command, msg) {
     var request = {
        "id": 42,
        "command": command,
        "params": msg
    };
    var message = JSON.stringify(request);
    self.websocket.send(message);

  }
}


