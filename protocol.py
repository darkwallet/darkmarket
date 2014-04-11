

def hello(data):
    data['type'] = 'hello'
    return data

def ok():
    return {'type': 'ok'}

def shout(data):
    data['type'] = 'shout'
    return data
