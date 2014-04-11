

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

