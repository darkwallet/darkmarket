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
    #eligius_pushtx(raw_tx)
    #gateway_broadcast(raw_tx)
    #bci_pushtx(raw_tx)

