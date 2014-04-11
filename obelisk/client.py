import struct
from decimal import Decimal

from twisted.internet import reactor

from zmqbase import ClientBase

import bitcoin
import models
import serialize
import error_code

def unpack_error(data):
    value = struct.unpack_from('<I', data, 0)[0]
    return error_code.error_code.name_from_id(value)

def pack_block_index(index):
    if type(index) == str:
        assert len(index) == 32
        return serialize.ser_hash(index)
    elif type(index) == int:
        return struct.pack('<I', index)
    else:
        raise ValueError("Unknown index type")

class ObeliskOfLightClient(ClientBase):
    valid_messages = ['fetch_block_header', 'fetch_history', 'subscribe',
        'fetch_last_height', 'fetch_transaction', 'fetch_spend',
        'fetch_transaction_index', 'fetch_block_transaction_hashes',
        'fetch_block_height', 'fetch_stealth', 'update', 'renew']

    subscribed = 0
    # Command implementations
    def renew_address(self, address, cb=None):
        address_version, address_hash = \
            bitcoin.bc_address_to_hash_160(address)
        # prepare parameters
        data = struct.pack('B', address_version)          # address version
        data += address_hash[::-1]               # address

        # run command
        self.send_command('address.renew', data, cb)

    def subscribe_address(self, address, notification_cb=None, cb=None):
        address_version, address_hash = \
            bitcoin.bc_address_to_hash_160(address)
        # prepare parameters
        data = struct.pack('B', address_version)          # address version
        data += address_hash[::-1]               # address

        # run command
        self.send_command('address.subscribe', data, cb)
        if notification_cb:
            if not address_hash in self._subscriptions['address']:
                self._subscriptions['address'][address_hash] = []
            if not notification_cb in self._subscriptions['address'][address_hash]:
                self._subscriptions['address'][address_hash].append(notification_cb)

    def unsubscribe_address(self, address, subscribed_cb, cb=None):
        address_version, address_hash = \
            bitcoin.bc_address_to_hash_160(address)

        if address_hash in self._subscriptions['address']:
            if subscribed_cb in self._subscriptions['address'][address_hash]:
               self._subscriptions['address'][address_hash].remove(subscribed_cb)
               if len(self._subscriptions['address'][address_hash]) == 0:
                   self._subscriptions['address'].pop(address_hash)
        if cb:
            cb(None, address)

    def fetch_block_header(self, index, cb):
        """Fetches the block header by height."""
        data = pack_block_index(index)
        self.send_command('blockchain.fetch_block_header', data, cb)

    def fetch_history(self, address, cb, from_height=0):
        """Fetches the output points, output values, corresponding input point
        spends and the block heights associated with a Bitcoin address.
        The returned history is a list of rows with the following fields:
     
            output
            output_height
            value
            spend
            spend_height

        If an output is unspent then the input spend hash will be equivalent
        to null_hash.

        Summing the list of values for unspent outpoints gives the balance
        for an address."""
        address_version, address_hash = \
            bitcoin.bc_address_to_hash_160(address)
        # prepare parameters
        data = struct.pack('B', address_version)    # address version
        data += address_hash[::-1]                  # address
        data += struct.pack('<I', from_height)      # from_height

        # run command
        self.send_command('address.fetch_history', data, cb)

    def fetch_last_height(self, cb):
        """Fetches the height of the last block in our blockchain."""
        self.send_command('blockchain.fetch_last_height', cb=cb)

    def fetch_transaction(self, tx_hash, cb):
        """Fetches a transaction by hash."""
        data = serialize.ser_hash(tx_hash)
        self.send_command('blockchain.fetch_transaction', data, cb)

    def fetch_spend(self, outpoint, cb):
        """Fetches a corresponding spend of an output."""
        data = outpoint.serialize()
        self.send_command('blockchain.fetch_spend', data, cb)

    def fetch_transaction_index(self, tx_hash, cb):
        """Fetch the block height that contains a transaction and its index
        within a block."""
        data = serialize.ser_hash(tx_hash)
        self.send_command('blockchain.fetch_transaction_index', data, cb)

    def fetch_block_transaction_hashes(self, index, cb):
        """Fetches list of transaction hashes in a block by block hash."""
        data = pack_block_index(index)
        self.send_command('blockchain.fetch_block_transaction_hashes',
            data, cb)

    def fetch_block_height(self, blk_hash, cb):
        """Fetches the height of a block given its hash."""
        data = serialize.ser_hash(blk_hash)
        self.send_command('blockchain.fetch_block_height', data, cb)

    def fetch_stealth(self, prefix, cb, from_height=0):
        """Fetch possible stealth results. These results can then be iterated
        to discover new payments belonging to a particular stealth address.
        This is for recipient privacy.
        
        The prefix is a special value that can be adjusted to provide
        greater precision at the expense of deniability.
        
        from_height is not guaranteed to only return results from that
        height, and may also include results from earlier blocks.
        It is provided as an optimisation. All results at and after
        from_height are guaranteed to be returned however."""
        number_bits, bitfield = prefix
        data = struct.pack('<BII', number_bits, bitfield, from_height)
        assert len(data) == 9
        self.send_command('blockchain.fetch_stealth', data, cb)

    # receive handlers
    def _on_fetch_block_header(self, data):
        error = unpack_error(data)
        assert len(data[4:]) == 80
        header = data[4:]
        return (error, header)

    def _on_fetch_history(self, data):
        error = unpack_error(data)
        # parse results
        rows = self.unpack_table("<32sIIQ32sII", data, 4)
        history = []
        for row in rows:
            o_hash, o_index, o_height, value, s_hash, s_index, s_height = row
            o_hash = o_hash[::-1]
            s_hash = s_hash[::-1]
            if s_index == 4294967295:
                s_hash = None
                s_index = None
                s_height = None
            history.append(
                (o_hash, o_index, o_height, value, s_hash, s_index, s_height))
        return (error, history)

    def _on_fetch_last_height(self, data):
        error = unpack_error(data)
        height = struct.unpack('<I', data[4:])[0]
        return (error, height)

    def _on_fetch_transaction(self, data):
        error = unpack_error(data)
        tx = data[4:]
        return (error, tx)

    def _on_fetch_spend(self, data):
        error = unpack_error(data)
        spend = serialize.deser_output_point(data[4:])
        return (error, spend)

    def _on_fetch_transaction_index(self, data):
        error = unpack_error(data)
        height, index = struct.unpack("<II", data[4:])
        return (error, height, index)

    def _on_fetch_block_transaction_hashes(self, data):
        error = unpack_error(data)
        rows = self.unpack_table("32s", data, 4)
        hashes = [row[0][::-1] for row in rows]
        return (error, hashes)

    def _on_fetch_block_height(self, data):
        error = unpack_error(data)
        height = struct.unpack('<I', data[4:])[0]
        return (error, height)

    def _on_fetch_stealth(self, data):
        error = unpack_error(data)
        raw_rows = self.unpack_table("<33sB20s32s", data, 4)
        rows = []
        for ephemkey, address_version, address_hash, tx_hash in raw_rows:
            address = bitcoin.hash_160_to_bc_address(
                address_hash[::-1], address_version)
            tx_hash = tx_hash[::-1]
            rows.append((ephemkey, address, tx_hash))
        return (error, rows)
        
    def _on_subscribe(self, data):
        self.subscribed += 1
        error = unpack_error(data)
        if error:
            print "Error subscribing"
        if not self.subscribed%1000:
            print "Subscribed ok", self.subscribed
        return (error, True)

    def _on_update(self, data):
        address_version = struct.unpack_from('B', data, 0)[0]
        address_hash = data[1:21][::-1]
        address = bitcoin.hash_160_to_bc_address(address_hash, address_version)

        height = struct.unpack_from('I', data, 21)[0]
        block_hash = data[25:57]
        tx = data[57:]

        if address_hash in self._subscriptions['address']:
            for update_cb in self._subscriptions['address'][address_hash]:
                update_cb(address_version, address_hash, height, block_hash, tx)

    def _on_renew(self, data):
        self.subscribed += 1
        error = unpack_error(data)
        if error:
            print "Error subscribing"
        if not self.subscribed%1000:
            print "Renew ok", self.subscribed
        return (error, True)

