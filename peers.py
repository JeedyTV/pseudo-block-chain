import time
import requests
from collections import Counter
from requests.models import requote_uri
from blockchain import Block,Blockchain
from transaction import Transaction
from threading import Timer,Thread,Event
import json
from datetime import datetime 

class Peer:
    
    def __init__(self, address,miner,bootstrap=None,difficulty=None):
        """Represente a node in the network can interact with the other trought HTTP protocol

        Args:
            address (string): address of the node , Peer
            miner (Bool): True if it is a miner False otherwise
            bootstrap (string, optional): initial entry point of
            the bootstrapping procedure. Defaults to None.
            difficulty (int, optional): represent the difficulty of the store. Defaults to None.
        """
        self.address = address
        self.miner = miner
        self.mining = miner
        self.memoryPool = [] #represent the Pool of transaction in the network
        self.peers = [] #represent the set of neighbors known
        self.blockchain = None #store components
        self.ready = False # True if the node is ready to mining after the instantiation
        self.peers_heartbeat = [] #represent the set of neighbors known as still alive
        self.heartbeat_count = {} #list of number wich count the number of missing response for heartbeat.
        self.transactions_historic = [] #list of transaction added to the block
        self.nb_transactions = [] #used to plot the troughput
        self.timing = [] #used to plot the troughput
        self.start = datetime.now() #used to plot the troughput
        self.experiment_throughput = None #used to plot the troughput
        self.experiment_attacker = None #used to perform the 51% attack
        self.experiment_victim = None #used to perform the 51% attack

        #if first peer create a blockchain for the whole network
        if not bootstrap:
            # Initialize the chain with the Genesis block.
            b = Block(0,self.address,[],"0",time.asctime())
            self.blockchain = Blockchain(self,difficulty,b)
            self.ready = True
        else:
        # Bootstrap the chain with the specified bootstrap address.
            self.bootstrapProc(bootstrap)
        #start heartbeat procedure
        t = PerpetualTimer(3,self.heartbeat)
        t.start()

    def bootstrapProc(self, address):
            """Implements the bootstrapping procedure."""
            #ask to the boostrap node the list of peers
            try:
                response = requests.get(f'http://{address}/peers')
                if response.status_code == 200:
                    self.peers.append(address)
                    self.peers += response.json()
                    if self.address in self.peers:
                        self.peers.remove(self.address)
                else:
                    print("bootstrapping procedure cannot get peers")
                    return
                #ask to each node the size of the chain toi determine the longest
                chain_sizes = {}
                for peer in self.peers:
                    response = requests.get(f'http://{peer}/addNewNode?address={self.address}')
                    chain_sizes[peer] = response.json()

                #retrieve longest chain size in the network
                longestSize = max(chain_sizes.values())
                #retrieve a node with the longest chain size
                p = list(chain_sizes.keys())[list(chain_sizes.values()).index(longestSize)]
                #ask key chain to that node
                response = requests.get(f'http://{p}/keyChain')
                self.blockchain = Blockchain(self,response.json())
                #ask memoryPool to that node
                response = requests.get(f'http://{p}/memoryPool')
                for t in json.loads(response.json()):
                    self.memoryPool.append(Transaction(str(t).replace('\'','\"')))
                self.ready = True
            except Exception as e:
                print("impossible de contacter le noeud maybee crash ?")
                print(e)
                exit(1)

    def put(self, key, value, time,block=True):
            """Puts the specified key and value on the Blockchain.
            The block flag indicates whether the call should block until the value
            has been put onto the blockchain, or if an error occurred.
            """
            transaction = Transaction(self.address, key, value,time)
            #Add dans pool
            self.add_transaction(transaction)
            #start call back if asked
            if block:
                callback = Callback(transaction, self.blockchain)
                callback.wait()
                mess = f'({key}, {value}) added to the store at index {callback.index} at {callback.time}'
                print(mess)
                return mess
            mess = f'({key}, {value}) will eventually be added to the store'
            print(mess)
            return mess

    def add_transaction(self, transaction):
            """Adds a transaction to your current list of transactions,
            and broadcasts it to your Blockchain network.
            If the `mine` method is called, it will collect the current list
            of transactions, and attempt to mine a block with those.
            """
            if self.experiment_throughput:
                if (datetime.now() - self.start).seconds > 180:
                    print("-- Experiment Time > 180")
                    print("-- No transaction added anymore for the experiment.")
                    return
            #add in the pool if not same transaction and no already in the pool
            if transaction not in self.memoryPool and transaction not in self.transactions_historic:
                self.memoryPool.append(transaction)
                self.transactions_historic.append(transaction)
                self.broadcastTrans(transaction)
            else:
                #discard transaction
                pass
            #Broadcast
    
    def handle_memoryPool(self, block):
        """remove from the Pool the transactions mined

        Args:
            block (Block): block just received or mined
        """
        return_memoryPool = self.memoryPool.copy()
        for t in block.transactions:
            
            for t_mp in self.memoryPool: 
                if t.key == t_mp.key and t.value == t_mp.value \
                    and t.timestamp == t_mp.timestamp and \
                    t_mp in return_memoryPool:
                        return_memoryPool.remove(t_mp)

        self.memoryPool = return_memoryPool.copy()

    def consensus(self,block, address):
        """check if the node mine on purpose. if it do not do so it change its key chains
        with a good one

        Args:
            block (Block): block just received by the node
            address (string): address of the peer who mined the relative block

        Returns:
            Bool: True if we changed the chain False otherwise 
        """
        index_last_block = self.blockchain.last_block.index

        if block.index - index_last_block >= 2:

            try:
                response = requests.get(f'http://{address}/keyChain')
                self.blockchain = Blockchain(self,response.json())
                if self.experiment_victim:
                    print("\n\n########### HACKED :( ###########\n\n")
                return True

            except Exception:
                pass

        return False
    
    def broadcastTrans(self,transaction):
        """Broadcast transaction to all peers

        Args:
            transaction (Transaction): transaction we need to broadcast
        """
        for peer in self.peers:
            try:
                requests.get(f'http://{peer}/addTransaction?transaction={str(transaction)}')
            except Exception:
                pass

    def broadcastBlock(self,block):
        """Broadcast block to all peers

        Args:
            block (Block): block we need to broadcast
        """
        for peer in self.peers:
            try:
                requests.get(f'http://{peer}/addNewBlock?block={str(block)}')
            except Exception:
                pass

    def add_block (self, block):
        """check is the block is already in the chain if not so broadcast after added

        Args:
            block ([type]): block just received or mined we have to add to our chain
        """
        self.mining = False
        self.handle_memoryPool(block)
        
        if block not in self.blockchain.blocks:
           
            if(self.blockchain.add_block(block)):

                self.broadcastBlock(block)

        else:
            #DISCARD BLOCK
            pass
        self.mining = True

    def mine(self):
        """Implements the mining procedure."""
        
        #if the peer is not a miner we stop the function
        if not self.miner:
            return False
        
        a, b, c = self.mining, self.memoryPool == [], self.ready
        #check if the pool is empty and if the node msut mine
        if c and (not a or b):
            #if not he wait here
            time.sleep(2) # the recursion depht max 999 so we wait for 33 min of simulation max
            print("wait transaction in pool...")
            return self.mine()

        print(f"-- Start mining index {len(self.blockchain)}")
        
        mining_pool = self.memoryPool.copy()
        #create a new block to mined
        
        candidate_block = Block(len(self.blockchain.blocks),self.address, mining_pool, self.blockchain.last_block._hash,time.asctime())
        
        
        #start minig by computing the POW
        while True:
            
            if self.mining:
                if self.experiment_victim == True:
                    time.sleep(5)
                    # if 51% remove puissance to the node by slowing it down
                     
                
                hash = candidate_block._hash
                #if POW fined we broadcast each node to the peers
                if hash.startswith('0' * self.blockchain.difficulty):

                    if self.experiment_throughput:
                        if len(self.nb_transactions) == 0:
                            self.nb_transactions.append(len(candidate_block.transactions))
                        else:
                            self.nb_transactions.append(len(candidate_block.transactions) + self.nb_transactions[-1])                        
                        self.timing.append((datetime.now() - self.start).seconds)
                        print("Nb transactions:")
                        print(self.nb_transactions)
                        print("Timing:")
                        print(self.timing)
                    
                    self.blockchain.add_block(candidate_block)
                    self.handle_memoryPool(candidate_block)
                    
                    for peer in self.peers:
                        try:
                            print("Broadcast à peer " + peer)
                            requests.get(f'http://{peer}/addNewBlock?block={str(candidate_block)}')
                
                        except Exception:
                            pass

                    print("-- End mining --")

                    return self.mine()
            
                candidate_block.nonce += 1
            else:
                return self.mine()
            
    def retrieve(self, key):
            """Searches the most recent value of the specified key.

            -> Search the list of blocks in reverse order for the specified key,
            or implement some indexing schemes if you would like to do something
            more efficient.
            """
            latest_value = None
            for b in self.blockchain.blocks:
                for t in b.transactions:
                    if(t.key == key):
                        latest_value = (t.value,t.origin,t.timestamp)

            if latest_value != None:
                print("Latest value for the key : "+key)
                print(latest_value)

            return latest_value

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        values = []

        for b in self.blockchain.blocks:
            for t in b.transactions:
                    if(t.key == key):
                        values.append((t.value,t.origin,t.timestamp))

        if values != []:
            print("Values for the key : "+key)
            print(values)

        return values
 
    def heartbeat(self, removed):
        """send a heartbeat to each peers to retrieve if it still alive.
        

        Args:
            removed (Bool): show if the peer was removed or not
        """
        try:
            if not removed:
                
                self.peers_heartbeat = self.peers.copy()
            
            for peer in self.peers_heartbeat:
                current_peer = peer
                requests.get(f'http://{peer}/heartbeat')
                self.heartbeat_count[peer] = 0

            
        except Exception:

            self.peers_heartbeat.remove(current_peer)
            self.heartbeat_count[current_peer] += 1

            if self.heartbeat_count[current_peer] == 10:
                self.peers.remove(current_peer)
                del self.heartbeat_count[current_peer]

            self.heartbeat(1)

    def __str__(self) -> str:
        return f'\"{self.address}\"'
        
    def __repr__(self) -> str:
        return f'\"{self.address}\"'
     
class Callback:
    #called whenever the key has been added to the system, or if a failure occurred.
    
    def __init__(self, transaction, blockchain):
        self.transaction = transaction
        self.blockchain = blockchain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        while True:
            if self.completed():
                return True

    def completed(self):
        """Polls the blockchain to check if the data is available."""
        for block in self.blockchain.blocks:
            if block.contains(self.transaction):
                self.time = block.timestamp
                self.index = block.index
                return True
        return False

class PerpetualTimer():
    """permit to create thread and relaunch a function with some time interval"""
    
    def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)
      self.thread.daemon = True

    def handle_function(self):
        self.hFunction(0)
        self.thread = Timer(self.t,self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

    