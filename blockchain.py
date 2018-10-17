"""
The basic architecture of the blockchain is inspired by this tutorial:
https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
and has been extended to store local updates of a FL model.
"""
import hashlib
import json
import time
from flask import Flask,jsonify,request
from uuid import uuid4
from urlparse import urlparse
import requests
import random
from threading import Thread, Event


class Blockchain(object):
    def __init__(self):
        super(Blockchain,self).__init__()
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()
        self.accepting = True

    def register_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def new_block(self,proof,previous_hash=None):
        block = {
            'index':len(self.chain)+1,
            'timestamp':time.time(),
            'transactions':self.current_transactions,
            'proof':proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transaction(self,sender,recipient,amount):
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })
        return self.last_block['index']+1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        return self.chain[-1]


    def proof_of_work(self,stop_event):#,last_proof):
        last_proof = self.last_block['proof']
        proof = random.randint(0,100000000)
        while ((not stop_event.is_set())
            and self.valid_proof(last_proof,proof) is False):
            proof += 1
            if proof%1000==0:
                print("mining",proof)
            last_proof = self.last_block['proof']
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        guess = '{last_proof}{proof}'.format(last_proof=last_proof,proof=proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        k = "00000000"
        return guess_hash[:len(k)] == k


    def valid_chain(self,chain):
        last_block = chain[0]
        curren_index = 1
        while curren_index<len(chain):
            block = chain[curren_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'],block['proof']):
                return False
            last_block = block
            curren_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get('http://{node}/chain'.format(node=node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length>max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False
