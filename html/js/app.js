angular.module('app', [])

angular.module('app').directive('identicon', function () {
    return {
      restrict: 'E', // element
      scope: {
        hash: '=',
        iconSize: '='
      },
      link: function(scope, element, attrs) {
        var iconSize = scope.iconSize || 32;

        // Create the identicon
        function createFromHex(dataHex) {
          var data = new Identicon(dataHex, iconSize).toString();
          element.html('<img class="identicon" src="data:image/png;base64,' + data + '">');
        }
        // Watch for hash changes
        scope.$watch('hash', function() {
          if (scope.hash) {
            var tohash = scope.hash.substring(32, 64)
            createFromHex(tohash);
          }
        })
      }
    }
  });

angular.module('app').controller('Market', ['$scope', function($scope) {

  $scope.page = false
  $scope.shouts = [];
  $scope.newShout = ""
  $scope.currentReviews = []
  $scope.myReviews = []
  $scope.createShout = function() {
     // launch a shout
     var newShout = {'type': 'shout', 'text': $scope.newShout}
     socket.send('shout', newShout)
     $scope.shouts.push(newShout)
     $scope.newShout = '';
  }

  $scope.peers = [];
  $scope.peerIds = [];
  $scope.reviews = {};
  $scope.awaitingShop = null;
  $scope.queryShop = function(peer) {
     $scope.awaitingShop = peer.pubkey;
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
      case 'reputation':
         $scope.parse_reputation(msg)
         break;
      default:
         console.log("unhandled message!",msg)
         break;
    }
  })

  var add_review = function(pubkey, review) {
    var found = false;
    if (!$scope.reviews.hasOwnProperty(pubkey)) {
        $scope.reviews[pubkey] = []
    }
    $scope.reviews[pubkey].forEach(function(_review) {
        if (_review.sig == review.sig && _review.subject == review.subject && _review.pubkey == review.pubkey) {
           found = true
        }
    });
    if (!found) {
        // check if the review is about me
        if ($scope.myself.pubkey == review.subject) {
            $scope.myReviews.push(review)
        }
        $scope.reviews[pubkey].push(review)
    }
  }

  // Peer information has arrived
  $scope.parse_reputation = function(msg) {
    msg.reviews.forEach(function(review) {
        add_review(msg.pubkey, review);
    });
    if (!$scope.$$phase) {
       $scope.$apply();
    }
  }

  $scope.parse_page = function(msg) {
    if (msg.pubkey != $scope.awaitingShop)
       return
    if (!$scope.reviews.hasOwnProperty(msg.pubkey)) {
        $scope.reviews[msg.pubkey] = []
    }
    $scope.currentReviews = $scope.reviews[msg.pubkey]
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
  $scope.review= {rating:5, text:""}
  $scope.addReview = function() {
     var query = {'type': 'review', 'pubkey': $scope.page.pubkey, 'text': $scope.review.text, 'rating': parseInt($scope.review.rating)}
     socket.send('review', query)

     $scope.review.rating = 5;
     $scope.review.text = '';
     $scope.showReviewForm = false;
  }
  // My information has arrived
  $scope.parse_myself = function(msg) {
    $scope.myself = msg;
    if (!$scope.$$phase) {
       $scope.$apply();
    }
    msg.reputation.forEach(function(review) {
       add_review($scope.myself.pubkey, review)
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
  $scope.search = ""
  $scope.searchNickname = function() {
     var query = {'type': 'search', 'text': $scope.search };
     socket.send('search', query)
     $scope.search = ""
  }

}])
