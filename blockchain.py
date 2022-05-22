from hashlib import sha256
import json
from transaction import Transaction

class Block(dict):
    
    def __init__(self,*args):
        """
        represente the block of the key value chain.
        Args:
            index (int): index of the block in the key chain
            address (string) : address of the block who have created the block
            transactions ([Transaction]): List of Transaction in the block each element has the type Transaction
            previous_hash (string): hash of the block index - 1
            timestamp (type): time at which the block was created
        """
        #first constructor instantiate from 5 attribut nonce is 0 by default
        if len(args)==5: 
            self.index = args[0]
            self.address = args[1]
            self.transactions = args[2]
            self.previous_hash = args[3]
            self.timestamp = args[4]
            self.nonce = 0
            dict.__init__(self,index=args[0],address=args[1],transactions=args[2],\
                previous_hash=args[3],timestamp=args[4],nonce=0)
        #second constructor instantiate from a json like string
        elif len(args)==1:
            b = json.loads(args[0])
            self.index = b['index']
            self.address = b['address']
            transactions = []
            for t in b['transactions']:
                transactions.append(Transaction(str(t).replace('\'','\"')))
            self.transactions = transactions
            self.previous_hash = b['previous_hash']
            self.timestamp = b['timestamp']
            self.nonce = b['nonce']
            dict.__init__(self,index=b['index'],address=b['address'],transactions=transactions,\
                previous_hash=b['previous_hash'],timestamp=b['timestamp'],nonce=b['nonce'])

    @property
    def _hash(self):
        """compute the hash of the block based on the different attributes

        Returns:
            string: the hash
        """
        
        block_string = json.dumps(self.__dict__, sort_keys=True)
        
        hash = sha256(block_string.encode()).hexdigest()
        return hash

    def contains(self, transaction):
        """Returns a boolean expressing wether or not 
        the transaction is contained in the block.
        Args:
            transaction (Transaction): given transaction to look for.

        Returns:
            Bool: True if transaction is in the the block False otherwise
        """
        return transaction in self.transactions
    
    def __str__(self) -> str:
        return str(self.__dict__).replace('\'','\"')
        
    def __repr__(self) -> str:
        return str(self.__dict__).replace('\'','\"')
    
    def __eq__(self, __o: object) -> bool:
        
        if self.index == __o.index and self.transactions == __o.transactions and \
            self.previous_hash ==__o.previous_hash and self.timestamp == __o.timestamp \
            and self.address == __o.address and self.nonce == __o.nonce:
           return True
        else:
            return False

class Blockchain:

    def __init__(self,*args):
        """represents the store component of the key value store app.
        Args:
            peer (string): The peer associated to the chain
            difficulty (int): Difficulty of the Mine operation
            blocks ([Block]): List of blocks in the chain. each element are Block type.
        """
        #first constructor instantiate from 3 attribut
        if len(args)==3:
            self.peer = args[0]
            self.difficulty = args[1]
            self.blocks = [args[2]]
        #second constructor instantiate from a json like string
        elif len(args)==2:
            c = json.loads(args[1])
            self.peer = args[0]
            self.difficulty = c['difficulty']
            self.blocks = []
            for b in c['blocks']:
                self.blocks.append(Block(str(b).replace('\'','\"')))
    
    def __len__(self):
        """compute the actual length of the block chain.

        Returns:
            int: int representing the size of the key value chain
        """
        return len(self.blocks)

    @property
    def last_block(self):
        """retrieve th last block of the key value store

        Returns:
            Block: return the last block added to the chain
        """
        return self.blocks[-1]

    def add_block(self, block):
        """check if the block is valid and if so add to the store.

        Args:
            block (Block): Block that could be add to the store

        Returns:
            Bool: True if the block was added False otherwise
        """
        #Is previous hash the correct one ?
        
        if not block.previous_hash == self.last_block._hash:
            return False
        #Is proof valid ?
        if not block._hash.startswith('0' * self.difficulty):
            return False
        self.blocks.append(block)
        return True

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        
        Returns:
            Bool: True if the chain is valid False otherwise
        """

        previous_block = self.blocks[0]
        
        i = 1

        while i < len(self.blocks):
            
            block = self.blocks[i]

            #Is previous hash the correct one ?
            if not block.previous_hash == previous_block._hash:
                return False
            #Is proof valid ?
            if not block._hash.startswith('0' * self.difficulty):
                return False
            
            previous_block = block
            i += 1

        return True
    
    def __repr__(self) -> str:
        return str(self.__dict__).replace('\'','\"')
        
    def __str__(self) -> str:
        return str(self.__dict__).replace('\'','\"')
    
    def __eq__(self, __o: object) -> bool:
        
        return self.difficulty == __o.difficulty and self.blocks == __o.blocks
