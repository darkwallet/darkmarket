import obelisk
import sys
import threading
import urllib2, re, random

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

def broadcast(self, tx):
    raw_tx = tx.serialize().encode("hex")
    print "Tx data:", raw_tx
    eligius_pushtx(raw_tx)
    bci_pushtx(raw_tx)

