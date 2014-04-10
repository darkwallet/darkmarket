import zmq
import sys

class Acceptor:

    def __init__(self):
        self.blocks = []
        self.processor = []

    def accept(self, block):
        self.processor.append(block)

    def update(self):
        process = self.processor
        self.processor = []
        for block in self.processor:
            self.process(block)

    def process(self):
        # check hash of keys + values matches root hash
        # fetch tx height/index associated with block
        # compare to list
        # remove all items higher from blocks and kv map
        #
        pass

class Pool:

    def __init__(self, acceptor):
        self.txs = []
        self.acceptor = acceptor

    def add(self, tx):
        self.txs.append(tx)
        # add timeout/limit logic here.
        # for now create new block for every new registration.
        self.fabricate_block()

    def fabricate_block(self):
        txs = self.txs
        self.txs = []
        block = Block(txs)
        block.register()
        self.acceptor.accept(block)

class Block:

    def __init__(self, txs):
        self.txs = txs

    def register(self):
        pass

def main(argv):
    context = zmq.Context()
    recvr = context.socket(zmq.PULL)
    recvr.bind("tcp://*:5557")
    while True:
        name_reg = recvr.recv()
        value = recvr.recv()
        print name_reg, value

if __name__ == "__main__":
    main(sys.argv)

