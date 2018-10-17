"""
 - Federated Learning with Blockchain -
Mining script that implements the blockchain for FL
"""

import hashlib
import json
import time
from flask import Flask,jsonify,request
from uuid import uuid4
from urlparse import urlparse
import requests
import random
from blockchain import Blockchain
from threading import Thread, Event


class PoWThread(Thread):
    def __init__(self, stop_event,blockchain,node_identifier):
        self.stop_event = stop_event
        Thread.__init__(self)
        self.blockchain = blockchain
        self.node_identifier = node_identifier
        self.response = None

    def run(self):
        last_block = self.blockchain.last_block
        last_proof = last_block['proof']
        proof = self.blockchain.proof_of_work(self.stop_event)#last_proof)
        self.blockchain.new_transaction(
            sender='0',
            recipient=self.node_identifier,
            amount=1
        )
        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof,previous_hash)
        self.response = {
            'message':"New block forged",
            'index':block['index'],
            'transactions':block['transactions'],
            'proof':block['proof'],
            'previous_hash':block['previous_hash']
        }
        on_end_mining()


STOP_EVENT = Event()

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
blockchain = Blockchain()
receiving = True
status = {'s':"receiving"}

@app.route('/mine',methods=['GET'])
def mine():
    STOP_EVENT.clear()
    thread = PoWThread(STOP_EVENT,blockchain,node_identifier)
    status['s'] = "mining"
    thread.start()
    response = {'message': "Start mining"}
    return jsonify(response),200

def on_end_mining():
    status['s'] = "receiving"
    # send block to others..

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
    response = {'message': "Transaction will be added to block {index}".format(index=index)}
    return jsonify(response),201


@app.route('/status',methods=['GET'])
def get_status():
    response = {'status': status['s']}
    return jsonify(response),200

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain':blockchain.chain,
        'length':len(blockchain.chain)
    }
    return jsonify(response),200

@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message':"New nodes have been added",
        'total_nodes':list(blockchain.nodes)
    }
    return jsonify(response),201

@app.route('/nodes/resolve',methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/stopmining',methods=['GET'])
def stop_mining():
    if blockchain.resolve_conflicts():
        STOP_EVENT.set()
    response = {
        'mex':"stopped!"
    }
    return jsonify(response),200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-g', '--genesis', default=0, type=int, help='instantiate genesis block')
    parser.add_argument('-mh', '--mhost', help='other miner IP address')
    parser.add_argument('-mp', '--mport', help='other miner port')
    args = parser.parse_args()
    if args.genesis==0 and (args.mhost==None or args.mport==None):
        raise ValueError("Must set genesis=1 or specify mhost and mport")
    port = args.port
    app.run(host="localhost",port=port)
