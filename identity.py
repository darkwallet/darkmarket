import zmq
import sys
import hashlib
import obelisk
import broadcast
import forge
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

class Blockchain:

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

    def process(self, block):
        print "Processing block..."
        if not block.verify():
            # Invalid block so reject it.
            print >> sys.stderr, "Rejecting invalid block."
            return
        # check hash of keys + values matches root hash
        # fetch tx height/index associated with block
        # compare to list
        # remove all items higher from blocks and kv map
        #
        pass

    def postpone(self, block):
        # readd for later processing
        self.accept(block)

class Pool:

    def __init__(self, chain):
        self.txs = []
        self.chain = chain

    def add(self, tx):
        self.txs.append(tx)
        # add timeout/limit logic here.
        # for now create new block for every new registration.
        self.fabricate_block()

    def fabricate_block(self):
        print "Fabricating new block!"
        txs = self.txs
        self.txs = []
        block = Block(txs)
        block.register()
        self.chain.accept(block)

class Block:

    def __init__(self, txs, header=None):
        self.txs = txs
        self.header = None

    def register(self):
        # register block in the bitcoin blockchain
        root_hash = self.calculate_root_hash()
        # create tx with root_hash as output
        tx_hash = forge.send_root_hash(root_hash)
        self.header = (tx_hash, root_hash)

    def calculate_root_hash(self):
        h = hashlib.new("ripemd160")
        for key, value in self.txs:
            h.update(key)
            h.update(value)
        return h.digest()

    def verify(self):
        if self.header is None or len(self.header) != 2:
            return False
        root_hash = self.calculate_root_hash()
        return self.header[1] == root_hash

class ZmqPoller:

    def __init__(self, pool):
        self.pool = pool
        self.context = zmq.Context()
        self.recvr = self.context.socket(zmq.PULL)
        self.recvr.bind("tcp://*:5557")

    def update(self):
        try:
            name_reg = self.recvr.recv(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            return
        value = self.recvr.recv()
        self.pool.add((name_reg, value))

def main(argv):
    chain = Blockchain()
    pool = Pool(chain)
    zmq_poller = ZmqPoller(pool)
    lc_zmq = LoopingCall(zmq_poller.update)
    lc_zmq.start(0.1)
    lc_chain = LoopingCall(chain.update)
    lc_chain.start(6)
    reactor.run()
    return

if __name__ == "__main__":
    main(sys.argv)

