angular.module('app', [])

angular.module('app').controller('Market', ['$scope', function($scope) {

  $scope.page = false
  $scope.shouts = [];
  $scope.newShout = ""
  $scope.reviews = []
  $scope.createShout = function() {
     // launch a shout
     var newShout = {'type': 'shout', 'text': $scope.newShout}
     socket.send('shout', newShout)
     $scope.shouts.push(newShout)
     $scope.newShout = '';
  }

  $scope.peers = [];
  $scope.peerIds = [];

  $scope.queryShop = function(peer) {
     var query = {'type': 'query_page', 'pubkey': peer.pubkey}
     socket.send('query_page', query)
  }

 // Open the websocket connection and handle messages
  var socket = new Connection(function(msg) {
   switch(msg.type) {
      case 'peer':
         $scope.parse_peer(msg)
         break;
      case 'page':
         $scope.parse_page(msg)
         break;
      case 'myself':
         $scope.parse_myself(msg)
         break;
      case 'shout':
         $scope.parse_shout(msg)
         break;
    }
  })


  // Peer information has arrived
  $scope.parse_page = function(msg) {
    console.log("page!", msg)
    $scope.page = msg
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }
  $scope.parse_peer = function(msg) {
    if ($scope.peerIds.indexOf(msg.uri) == -1) {
      $scope.peers.push(msg)
      $scope.peerIds.push(msg.uri)
    }
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }
  // My information has arrived
  $scope.parse_myself = function(msg) {
    $scope.myself = msg;
    if (!$scope.$$phase) {
       $scope.$apply();
    }
    msg.reputation.forEach(function(review) {
       $scope.reviews.push(review)
    });
    msg.peers.forEach(function(peer) {
       $scope.parse_peer(peer)
    });
  }
  // A shout has arrived
  $scope.parse_shout = function(msg) {
    $scope.shouts.push(msg)
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }

 console.log("going!!")

}])
