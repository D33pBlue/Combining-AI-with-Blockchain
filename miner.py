"""
 - Federated Learning with Blockchain -
Mining script that implements the blockchain for FL
"""

import hashlib
import json
import time
from flask import Flask,jsonify,request
from uuid import uuid4
import requests
import random
import pickle
from blockchain import Blockchain
from threading import Thread, Event
from nn import *
import numpy as np


def make_base():
    reset()
    dataset = None
    with open("data/d0.d",'rb') as f:
        dataset = pickle.load(f)
    worker = NNWorker(dataset["train_img"],
        dataset["train_lab"],
        dataset["test_img"],
        dataset["test_lab"],
        0,
        "base0")
    worker.build_base()
    model = dict()
    model['model'] = worker.get_model()
    model['accuracy'] = worker.evaluate()
    worker.close()
    return model


class PoWThread(Thread):
    def __init__(self, stop_event,blockchain,node_identifier):
        self.stop_event = stop_event
        Thread.__init__(self)
        self.blockchain = blockchain
        self.node_identifier = node_identifier
        self.response = None

    def run(self):
        block,stopped = self.blockchain.proof_of_work(self.stop_event)
        self.response = {
            'message':"End mining",
            'stopped': stopped,
            'block': str(block)
        }
        on_end_mining(stopped)


STOP_EVENT = Event()

app = Flask(__name__)
status = {
    's':"receiving",
    'id':str(uuid4()).replace('-',''),
    'blockchain': None,
    'address' : ""
    }

@app.route('/mine',methods=['GET'])
def mine():
    STOP_EVENT.clear()
    thread = PoWThread(STOP_EVENT,status["blockchain"],status["id"])
    status['s'] = "mining"
    thread.start()
    response = {'message': "Start mining"}
    return jsonify(response),200

def on_end_mining(stopped):
    if status['s'] == "receiving":
        return
    if stopped:
        status["blockchain"].resolve_conflicts()
    status['s'] = "receiving"
    for node in status["blockchain"].nodes:
        requests.get('http://{node}/stopmining'.format(node=node))

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    if status['s'] != "receiving":
        return 'Miner not receiving', 400
    values = request.get_json()
    required = ['client','baseindex','update','datasize','computing_time']
    if not all(k in values for k in required):
        return 'Missing values', 400
    if client in status['blockchain'].current_updates:
        return 'Model already stored', 400
    index = blockchain.new_update(values['client'],
        values['baseindex'],
        values['update'],
        values['datasize'],
        values['computing_time'])
    for node in status["blockchain"].nodes:
        requests.post('http://{node}/transactions/new'.format(node=node),
            json=request.get_json())
    response = {'message': "Update will be added to block {index}".format(index=index)}
    return jsonify(response),201

@app.route('/status',methods=['GET'])
def get_status():
    response = {'status': status['s']}
    return jsonify(response),200

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain':[str(x) for x in status['blockchain'].chain],
        'length':len(status['blockchain'].chain)
    }
    return jsonify(response),200

@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        if node!=status['address'] and not node in status['blockchain'].nodes:
            status['blockchain'].register_node(node)
            for miner in status['blockchain'].nodes:
                if miner!=node:
                    print("node",node,"miner",miner)
                    requests.post('http://{miner}/nodes/register'.format(miner=miner),
                        json={'nodes': [node]})
    response = {
        'message':"New nodes have been added",
        'total_nodes':list(status['blockchain'].nodes)
    }
    return jsonify(response),201

@app.route('/nodes/resolve',methods=["GET"])
def consensus():
    replaced = status['blockchain'].resolve_conflicts()
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
    if status['blockchain'].resolve_conflicts():
        STOP_EVENT.set()
    response = {
        'mex':"stopped!"
    }
    return jsonify(response),200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-i', '--host', default='127.0.0.1', help='IP address of this miner')
    parser.add_argument('-g', '--genesis', default=0, type=int, help='instantiate genesis block')
    parser.add_argument('-ma', '--maddress', help='other miner IP:port')
    args = parser.parse_args()
    address = "{host}:{port}".format(host=args.host,port=args.port)
    status['address'] = address
    if args.genesis==0 and args.maddress==None:
        raise ValueError("Must set genesis=1 or specify maddress")
    if args.genesis==1:
        model = make_base()
        print("base model accuracy:",model['accuracy'])
        status['blockchain'] = Blockchain(status['id'],model,True)
    else:
        status['blockchain'] = Blockchain(status['id'])
        status['blockchain'].register_node(args.maddress)
        requests.post('http://{node}/nodes/register'.format(node=args.maddress),
            json={'nodes': [address]})
        status['blockchain'].resolve_conflicts()
    app.run(host=args.host,port=args.port)
