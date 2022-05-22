from peers import Peer
from transaction import Transaction
from blockchain import  Block,Blockchain

""" TESTING TRANSACTION """

#instantiate transaction 
t1 = Transaction('l:500','ab','cd','mtn')

"""
t1 is a transaction. should be represented as a json as follows:
"""
t1_as_string = '{"origin": "l:500", "key": "ab", "value": "cd", "timestamp": "mtn"}'
test_1 = str(t1) == t1_as_string

"""
t2 should be a twin of t1 as it is instantiate with a json representation of t1
"""
t2 = Transaction(str(t1))
test_2 = (t2 == t1)


print(f"test 1 :{test_1}")
print(f"test 2 :{test_2}")

""" END TESTING TRANSACTION """

""" TESTING BLOCK """

#instantiate block 
b1 = Block(0,'l:5000',[t1,t2],"0","mtn")

#check if when the nonce is changed hash is changed

h1 = b1._hash
b1.nonce += 1
h2 = b1._hash

test_3 = (h1 != h2)

"""
b1 is a block. should be represented as a json as follows:
"""
b1_as_string = '{"index": 0, "address": "l:5000", "transactions": [{"origin": "l:500", "key": "ab", "value": "cd", "timestamp": "mtn"}, {"origin": "l:500", "key": "ab", "value": "cd", "timestamp": "mtn"}], "previous_hash": "0", "timestamp": "mtn", "nonce": 1}' 
test_4 = (str(b1) == b1_as_string)

"""
b2 should be a twin of b1 as it is instantiate with a json representation of b1
"""
b2 = Block(str(b1))
test_5 = (b2 == b1)

"""each element of the attribut transactions of block should be a transaction"""
test_6 = []
for t in b1.transactions:
    test_6.append(isinstance(t,Transaction))
test_6 = False not in test_6
test_7 = []
for t in b2.transactions:
    test_7.append(isinstance(t,Transaction))
test_7 = False not in test_7

test_8 = b1.contains(t1)

print(f"test 3 :{test_3}")
print(f"test 4 :{test_4}")
print(f"test 5 :{test_5}")
print(f"test 6 :{test_6}")
print(f"test 7 :{test_7}")
print(f"test 8 :{test_8}")

""" END TESTING BLOCK """

""" TESTING BLOCKCHAIN """

#instantiate blockchain
c1 = Blockchain('l:23',1,b1)
"""
c1 is a blockchain. should be represented as a json as follows:
"""
c1_as_string = '{"peer": "l:23", "difficulty": 1, "blocks": [{"index": 0, "address": "l:5000", "transactions": [{"origin": "l:500", "key": "ab", "value": "cd", "timestamp": "mtn"}, {"origin": "l:500", "key": "ab", "value": "cd", "timestamp": "mtn"}], "previous_hash": "0", "timestamp": "mtn", "nonce": 1}]}' 
test_9 = (str(c1) == c1_as_string)

"""
c2 should be a twin of c1 as it is instantiate with a json representation of c1
"""
c2 = Blockchain('l:24',str(c1))
test_10 = (c2 == c1)

"""each element of the attribut blocks of blockchain should be a block"""
test_11 = []
for b in c1.blocks:
    test_11.append(isinstance(b,Block))
test_11 = False not in test_11

test_12 = []
for b in c2.blocks:
    test_12.append(isinstance(b,Block))
test_12 = False not in test_12

#at this point size of chain is 1
test_13 = len(c1) == 1

#try to add a block to the chain
new_block = Block(len(c1.blocks),"l:500",[t1,t2], c1.last_block._hash,"mtn")
        
while True: 
    if new_block._hash.startswith('0' * c1.difficulty):
        c1.add_block(new_block)
        break    
    new_block.nonce += 1

#at this point chain should be valid and len = 2

test_14 = len(c1) == 2

#test of the valid function
test_15 = c1.is_valid()

#test of the POW algo
#Is previous hash the correct one ?
test_16 = True
if not new_block.previous_hash == b1._hash:
    test_16 &= False
#Is proof valid ?
if not new_block._hash.startswith('0' * c1.difficulty):
    test_16 &= False

test_16 &= True

print(f"test 9 :{test_9}")
print(f"test 10 :{test_10}")
print(f"test 11 :{test_11}")
print(f"test 12 :{test_12}")
print(f"test 13 :{test_13}")
print(f"test 14 :{test_14}")
print(f"test 15 :{test_15}")
print(f"test 16 :{test_16}")

""" END TESTING BLOCKCHAIN """

""" TESTING PEER """

p = Peer(f'localhost:{5000}',False,difficulty=5)

p.add_transaction(t1)
#at this step size of Pool = 1
test_17 = len(p.memoryPool) == 1

p.add_transaction(t1)
#at this step size of Pool = 1
test_18 = len(p.memoryPool) == 1

#new transaction with rewrite of a key
t3 = Transaction('l:500','ab','CD','mtn2')
p.add_transaction(t3)

#at this step size of Pool = 2
test_19 = len(p.memoryPool) == 2

print(f"test 17 :{test_17}")
print(f"test 18 :{test_18}")
print(f"test 19 :{test_19}")

#other components can't be tested without instantiate a network.

""" END TESTING PEER """


