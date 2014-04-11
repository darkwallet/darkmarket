import obelisk

class Multisig:

    def __init__(self, number_required, pubkeys):
        self.number_required = number_required
        self.pubkeys = pubkeys

    @property
    def address(self):
        pass

    def create_transaction(self, outputs):
        # Returns transaction
        pass

    def sign(self, tx, secret):
        # Mutates tx
        pass

def Escrow:

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
    return

if __name__ == "__main__":
    main()

