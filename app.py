import argparse
from blockchain import Block
from flask import Flask, render_template,request,jsonify
from peers import Peer
from logo import LOGO
from transaction import Transaction
import json
import time
import threading 
from threading import Timer,Thread,Event


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=str, default='False', 
                        help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str,default=None,
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    parser.add_argument("--port", type=int,required=True,help="")

    parser.add_argument("--throughput", type=str,default='False',help="")

    parser.add_argument("--attack", type=str,default='False',help="")

    parser.add_argument("--victim", type=str,default='False',help="")

    arguments, _ = parser.parse_known_args()

    return arguments

app = Flask(__name__)

@app.route('/',methods=['post', 'get'])
def index():
    """handle the API for user interface

    Returns:
        string: html script
    """
    
    if request.method == 'POST':
        #add transaction to the system
        if request.form.get('s'):
            value = request.form.get('value')  # access the data inside 
            key = request.form.get('key')
            call =  request.form.get('callback')
            if call :
                message = p.put(key,value,time.asctime(),True) # add call back to user
            else:
                message = p.put(key,value,time.asctime(),False)  
            return render_template('index.html',message=message)
        
        #retrieve the value for specified key
        if request.form.get('RETRIEVE'):
            key = request.form.get('key')
            retrieved_key = p.retrieve(key)
            if retrieved_key == None:
                return render_template('index.html',No_value = key)
            return render_template('index.html',retrieve_key = retrieved_key)
        
        #retrieve values for specified key
        if request.form.get('RETRIEVE ALL'):
            key = request.form.get('key')
            retrieved_keys = p.retrieve_all(key)
            if retrieved_keys == []:
                return render_template('index.html',No_value = key)
            return render_template('index.html',retrieve_keys = retrieved_keys)
        
        #show the network of the user
        if request.form.get('NETWORK'):
            if p.peers ==  []:
                return render_template('index.html',noPeer="yes")
            return render_template('index.html',p=p.peers)
        
    return render_template('index.html')

@app.route('/testing',methods=['post', 'get'])
def index2():
    """used in test purposes add transaction trought a testing.py script
    """
    data = request.get_json(force=True)
    key = data['key']
    value = data['value']
    p.put(key,value,time.asctime(),False)
        
    return {}

@app.route('/peers')
def send_peers():
    #return the list of peers
    return jsonify(p.peers)

@app.route('/addNewNode')
def addNewNode():
    #add new peers to the peers list and send the size of it key chain
    new_peer= request.args.get('address')
    if new_peer not in p.peers:
        p.peers.append(new_peer)
        p.heartbeat_count[new_peer] = 0
    return jsonify(len(p.blockchain))

@app.route('/keyChain')
def send_keyChain():
    #send the key chain to a peers
    return jsonify(str(p.blockchain))

@app.route('/memoryPool')
def sendMemoryPool():
    #send the memory pool to a peer
    return jsonify(str(p.memoryPool))

@app.route('/addTransaction')
def newTransaction():
    #add a transaction to the Pool, transaction always comes from a peer of the network
    t = request.args.get('transaction').replace("\'",'\"')
    p.add_transaction(Transaction(t))
    return jsonify({})

@app.route('/heartbeat')
def send_heartbeat():
    return jsonify({'address': p.address})
  
@app.route('/addNewBlock')
def addNewBlock():
    #add a block mined to the chain if its correct
    
    #if in 51% attack discard all block
    if p.experiment_attacker == True:
        return jsonify(dict())
    else:
        b = request.args.get('block').replace("\'",'\"')
        #stop mining and asking if we mine the good next block via consensus
        print("stop mining")
        p.mining = False

        bl = Block(b)
        address = bl.address
        # si consensus False (pas de consensus), pas de probleme tu peux add 
        if not p.consensus(bl,address):
            p.add_block(bl)
            p.mining = True

    return jsonify(dict())

if __name__ == "__main__":
    arguments = parse_arguments()
    
    port = arguments.port
    miner = False
    if arguments.miner == 'True':
        miner = True
    difficulty = arguments.difficulty
    bootstrap = arguments.bootstrap
    
    #if 51% attack , add transaction manually in the store \
    # that we will change during the attack
    if arguments.attack == 'True':
        if arguments.victim == 'True': #5000
            p = Peer(f'localhost:{port}',miner,difficulty=difficulty)
            p.experiment_victim = True
            p.blockchain.blocks[0].transactions.append(Transaction('l:500','ab','cd','mtn'))
            p.peers.append('localhost:5001')
            p.heartbeat_count['localhost:5001'] = 0

        else:  #5001
            p = Peer(f'localhost:{port}',miner,difficulty=difficulty)
            p.experiment_attacker = True
            p.blockchain.blocks[0].transactions.append(Transaction('l:500','modified','cd','mtn'))
            p.peers.append('localhost:5000')
            p.heartbeat_count['localhost:5000'] = 0
            
    else:

        if not bootstrap:
            #first peer
            p = Peer(f'localhost:{port}',miner,difficulty=difficulty)
        else:
            #bootstrap peer  
            p = Peer(f'localhost:{port}',miner,bootstrap=bootstrap)
        
        if arguments.throughput == 'True':
            p.experiment_throughput = True
    
    print(LOGO)
    #start thread for mining
    thread = threading.Timer(0, p.mine)
    thread.daemon = True
    thread.start()
    
    app.run(port=port)
    