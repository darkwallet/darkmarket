import obelisk
import sys
import threading
import urllib2, re, random
import websocket
import json

# Makes a request to a given URL (first argument) and optional params (second argument)
def make_request(*args):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0'+str(random.randrange(1000000)))]
    try:
        return opener.open(*args).read().strip()
    except Exception,e:
        try: p = e.read().strip()
        except: p = e
        raise Exception(p)

def bci_pushtx(tx):
    return make_request('http://blockchain.info/pushtx','tx='+tx)

def eligius_pushtx(tx):
    s = make_request('http://eligius.st/~wizkid057/newstats/pushtxn.php','transaction='+tx+'&send=Push')
    strings = re.findall('string[^"]*"[^"]*"',s)
    for string in strings:
        quote = re.findall('"[^"]*"',string)[0]
        if len(quote) >= 5: return quote[1:-1]

def gateway_broadcast(tx):
    ws = websocket.create_connection("ws://gateway.unsystem.net:8888/")
    request = {"id": 110, "command": "broadcast_transaction", "params": [tx]}
    ws.send(json.dumps(request))
    result =  ws.recv()
    response = json.loads(result)
    if response["error"] is not None:
        print >> sys.stderr, "Error broadcasting to gateway:", response["error"]
        return
    print "Sent"
    ws.close()

def broadcast(tx):
    raw_tx = tx.serialize().encode("hex")
    print "Tx data:", raw_tx
    #print "TEMP DISABLED BROADCAST"
    eligius_pushtx(raw_tx)
    gateway_broadcast(raw_tx)
    #bci_pushtx(raw_tx)

if __name__ == "__main__":
    raw_tx = "0100000001470b5d4fd9cdfbf7382f1823733cacaf2d23cdb38e282ae64180fddcf1185c6e010000006b483045022100d6aef5a66a588425485691532bbdd2ca9d88e6a7e199c8c81979b03a8a163246022004f1aae76a2b9202a7c1c042a085c8d1b356c81350c70f225b300e4b0c170ae90121034bd380ea13b5871968696d73a56e707859240b098f65b144322beb0e24ff3d3fffffffff020000000000000000166a144661376feb8c1324abceccfb9a3760bb999fd53680380100000000001976a914f5e58287166b8655c769b6bb6f3e2480a2c8cd2688ac00000000"
    gateway_broadcast(raw_tx)

