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
    raw_tx = "0100000001a0e98dd6f648975e5dd7f5a2da3f349b452e70f22e31ecdfe8614c0147713d78010000006b483045022100f5c924a09ae4a4516b49d7aecfd73373e08f6e519bb7988bf01076b6f414b181022071023f837404ea1879e38a95340a458edf4afb521775d8dba1f4ccc842514a1d0121034bd380ea13b5871968696d73a56e707859240b098f65b144322beb0e24ff3d3fffffffff020000000000000000166a14910715286f7c16988a5d0ae5a56364d2a01bce2960ea0000000000001976a914f5e58287166b8655c769b6bb6f3e2480a2c8cd2688ac00000000"
    gateway_broadcast(raw_tx)

