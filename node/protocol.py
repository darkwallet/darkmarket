

def hello(data):
    data['type'] = 'hello'
    return data

def ok():
    return {'type': 'ok'}

def shout(data):
    data['type'] = 'shout'
    return data

def reputation(pubkey, reviews):
    data = {}
    data['type'] = 'reputation'
    data['pubkey'] = pubkey.encode('hex')
    data['reviews'] = reviews
    return data

def query_reputation(pubkey):
    data = {}
    data['type'] = 'query_reputation'
    data['pubkey'] = pubkey.encode('hex')
    return data

def page(pubkey, text, signature):
    data = {}
    data['type'] = 'page'
    data['pubkey'] = pubkey.encode('hex')
    data['signature'] = signature.encode('hex')
    data['text'] = text
    return data

def query_page(pubkey):
    data = {}
    data['type'] = 'query_page'
    data['pubkey'] = pubkey.encode('hex')
    return data

def order(id, buyer, seller, state, text, escrows=[], tx=None):
    data = {}
    data['type'] = 'order'
    data['id'] = id
    # this is who signs
    data['buyer'] = buyer.encode('hex')
    # this is who the review is about
    data['seller'] = seller.encode('hex')
    # the signature
    data['escrows'] = escrows
    # the signature
    if data.get('tex'):
        data['tx'] = tx.encode('hex')
    # some text
    data['text'] = text
    # some text
    data['state'] = state # new -> accepted/rejected -> payed -> sent -> received
    return data


def negotiate_pubkey(nickname, ident_pubkey):
    data = {}
    data['type'] = 'negotiate_pubkey'
    data['nickname'] = nickname
    data['ident_pubkey'] = ident_pubkey.encode("hex")
    return data

def response_pubkey(nickname, pubkey, signature):
    data = {}
    data['type'] = "response_pubkey"
    data['nickname'] = nickname
    data['pubkey'] = pubkey.encode("hex")
    data['signature'] = signature.encode("hex")
    return data

