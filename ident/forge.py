import obelisk
import broadcast

secret = "8cd252b8a48abb98aed387b204a417ae38e4a928b0e997654bdd742dd044659c".decode("hex")
address = "1PRBVdCHoPPD3bz8sCZRTm6iAtuoqFctvx"
client = None

def hash_transaction(tx):
    return obelisk.Hash(tx.serialize())[::-1]

class HistoryCallback:

    def __init__(self, root_hash, finished_cb):
        self.root_hash = root_hash
        self.finished_cb = finished_cb

    def fetched(self, ec, history):
        if ec is not None:
            print >> sys.stderr, "Error fetching history:", ec
            return
        unspent_rows = [row[:4] for row in history if row[4] is None]
        unspent = build_output_info_list(unspent_rows)
        tx_hash = build_actual_tx(unspent, self.root_hash)
        self.finished_cb(tx_hash)

def send_root_hash(root_hash, finished_cb):
    global client
    if client is None:
        client = obelisk.ObeliskOfLightClient("tcp://obelisk.unsystem.net:9091")
    print "sending", root_hash.encode("hex")
    cb = HistoryCallback(root_hash, finished_cb)
    client.fetch_history(address, cb.fetched)

def build_actual_tx(unspent, root_hash):
    print "Building...", root_hash.encode("hex")
    fee = 10000
    optimal_outputs = obelisk.select_outputs(unspent, fee)
    tx = obelisk.Transaction()
    for output in optimal_outputs.points:
        add_input(tx, output.point)
    add_return_output(tx, root_hash)
    change = optimal_outputs.change
    add_output(tx, address, change)
    key = obelisk.EllipticCurveKey()
    key.set_secret(secret)
    for i, output in enumerate(optimal_outputs.points):
        obelisk.sign_transaction_input(tx, i, key)
    broadcast.broadcast(tx)
    tx_hash = hash_transaction(tx)
    return tx_hash

def add_input(tx, prevout):
    input = obelisk.TxIn()
    input.previous_output.hash = prevout.hash
    input.previous_output.index = prevout.index
    tx.inputs.append(input)

def add_return_output(tx, data):
    output = obelisk.TxOut()
    output.value = 0
    output.script = "\x6a\x14" + data
    tx.outputs.append(output)

def add_output(tx, address, value):
    output = obelisk.TxOut()
    output.value = value
    output.script = obelisk.output_script(address)
    tx.outputs.append(output)

def build_output_info_list(unspent_rows):
    unspent_infos = []
    for row in unspent_rows:
        assert len(row) == 4
        outpoint = obelisk.OutPoint()
        outpoint.hash = row[0]
        outpoint.index = row[1]
        value = row[3]
        unspent_infos.append(
            obelisk.OutputInfo(outpoint, value))
    return unspent_infos

if __name__ == "__main__":
    from twisted.internet import reactor
    client = obelisk.ObeliskOfLightClient("tcp://obelisk.unsystem.net:9091")
    client.fetch_history(address, history_fetched)
    reactor.run()

