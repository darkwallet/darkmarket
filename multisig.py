import obelisk
from twisted.internet import reactor

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

class Multisig:

    def __init__(self, client, number_required, pubkeys):
        if number_required > len(pubkeys):
            raise Exception("number_required > len(pubkeys)")
        self.client = client
        self.number_required = number_required
        self.pubkeys = pubkeys

    @property
    def script(self):
        result = chr(80 + self.number_required)
        for pubkey in self.pubkeys:
            result += chr(33) + pubkey
        result += chr(80 + len(self.pubkeys))
        # checkmultisig
        result += "\xae"
        return result

    @property
    def address(self):
        raw_addr = obelisk.hash_160(self.script)
        return obelisk.hash_160_to_bc_address(raw_addr, addrtype=0x05)

    def create_unsigned_transaction(self, destination, finished_cb):
        def fetched(ec, history):
            if ec is not None:
                print >> sys.stderr, "Error fetching history:", ec
                return
            self._fetched(history, destination, finished_cb)
        self.client.fetch_history(self.address, fetched)

    def _fetched(self, history, destination, finished_cb):
        unspent = [row[:4] for row in history if row[4] is None]
        tx = self._build_actual_tx(unspent, destination)
        finished_cb(tx)

    def _build_actual_tx(self, unspent, destination):
        # Send all unspent outputs (everything in the address) minus the fee
        tx = obelisk.Transaction()
        total_amount = 0
        for row in unspent:
            assert len(row) == 4
            outpoint = obelisk.OutPoint()
            outpoint.hash = row[0]
            outpoint.index = row[1]
            value = row[3]
            total_amount += value
            add_input(tx, outpoint)
        # Constrain fee so we don't get negative amount to send
        fee = min(total_amount, 10000)
        send_amount = total_amount - fee
        add_output(tx, destination, send_amount)
        return tx

    def sign_all_inputs(self, tx, secret):
        signatures = []
        key = obelisk.EllipticCurveKey()
        key.set_secret(secret)
        for i, input in enumerate(tx.inputs):
            sighash = generate_signature_hash(tx, i, self.script)
            # Add sighash::all to end of signature.
            signature = key.sign(sighash) + "\x01"
            signatures.append(signature)
        return signatures

def add_input(tx, prevout):
    input = obelisk.TxIn()
    input.previous_output.hash = prevout.hash
    input.previous_output.index = prevout.index
    tx.inputs.append(input)

def add_output(tx, address, value):
    output = obelisk.TxOut()
    output.value = value
    output.script = obelisk.output_script(address)
    tx.outputs.append(output)

def generate_signature_hash(parent_tx, input_index, script_code):
    tx = obelisk.copy_tx(parent_tx)
    if input_index >= len(tx.inputs):
        return None
    for input in tx.inputs:
        input.script = ""
    tx.inputs[input_index].script = script_code
    raw_tx = tx.serialize() + "\x01\x00\x00\x00"
    return obelisk.Hash(raw_tx)[::-1]

class Escrow:

    def __init__(self, buyer_pubkey, seller_pubkey, arbit_pubkey):
        pubkeys = (buyer_pubkey, seller_pubkey, arbit_pubkey)
        self.multisig = Multisig(2, pubkeys)

    @property
    def deposit_address(self):
        return self.multisig.address

    def release_funds(self, value):
        # Returns signed transaction
        pass

def main():
    pubkeys = [
        "035b175132eeb8aa6e8455b6f1c1e4b2784bea1add47a6ded7fc9fc6b7aff16700".decode("hex"),
        "0351e400c871e08f96246458dae79a55a59730535b13d6e1d4858035dcfc5f16e2".decode("hex"),
        "02d53a92e3d43db101db55e351e9b42b4f711d11f6a31efbd4597695330d75d250".decode("hex")
    ]
    client = obelisk.ObeliskOfLightClient("tcp://85.25.198.97:9091")
    msig = Multisig(client, 2, pubkeys)
    print msig.address
    def finished(tx):
        print tx
        print tx.serialize().encode("hex")
        sigs1 = msig.sign_all_inputs(tx, "b28c7003a7b6541cd1cd881928863abac0eff85f5afb40ff5561989c9fb95fb2".decode("hex"))
        sigs3 = msig.sign_all_inputs(tx, "b74dbef0909c96d5c2d6971b37c8c71d300e41cad60aeddd6b900bba61c49e70".decode("hex"))
        for i, input in enumerate(tx.inputs):
            sigs = (sigs1[i], sigs3[i])
            script = "\x00"
            for sig in sigs:
                script += chr(len(sig)) + sig
            script += "\x4c"
            assert len(msig.script) < 255
            script += chr(len(msig.script)) + msig.script
            print "Script:", script.encode("hex")
            tx.inputs[i].script = script
        print tx
        print tx.serialize().encode("hex")
    msig.create_unsigned_transaction("1Fufjpf9RM2aQsGedhSpbSCGRHrmLMJ7yY", finished)
    reactor.run()

if __name__ == "__main__":
    main()

