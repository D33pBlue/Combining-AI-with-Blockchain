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
from urllib.parse import urlparse
import requests
import random
from threading import Thread, Event


def compute_global_model(updates):
    accuracy = 0
    model = None
    return accuracy,model

def find_len(text,strk):
    return text.find(strk),len(strk)

class Update:
    def __init__(self,client,baseindex,update,datasize,computing_time,timestamp=time.time()):
        self.timestamp = timestamp
        self.baseindex = baseindex
        self.update = update
        self.client = client
        self.datasize = datasize
        self.computing_time = computing_time

    @staticmethod
    def from_string(updstr):
        i,l = find_len(updstr,"timestamp:")
        i2,l2 = find_len(updstr,"baseindex:")
        timestamp = float(updstr[i+l:i2])
        print(timestamp)

    def __str__(self):
        return "'timestamp': {timestamp},\
            'baseindex': {baseindex},\
            'update': {update},\
            'client': {client},\
            'datasize': {datasize},\
            'computing_time': {computing_time}".format(
                timestamp = self.timestamp,
                baseindex = self.baseindex,
                update = self.update,
                client = self.client,
                datasize = self.datasize,
                computing_time = self.computing_time
            )#.encode()


class Block:
    def __init__(self,miner,index,basemodel,accuracy,updates,proof,previous_hash):
        self.index = index
        self.miner = miner
        self.timestamp = time.time()
        self.basemodel = basemodel
        self.accuracy = accuracy
        self.updates = updates
        self.proof = proof
        self.previous_hash = previous_hash

    @staticmethod
    def from_string(updstr):
        i,l = find_len(updstr,"'timestamp':")
        i2,l2 = find_len(updstr,"'basemodel':")
        i3,l3 = find_len(updstr,"'index':")
        i4,l4 = find_len(updstr,"'miner':")
        i5,l5 = find_len(updstr,"'accuracy':")
        i6,l6 = find_len(updstr,"'updates':")
        i7,l7 = find_len(updstr,"'proof':")
        i8,l8 = find_len(updstr,"'previous_hash':")
        i9,l9 = find_len(updstr,"'updates_size':")
        index = int(updstr[i3+l3:i4].replace(",",'').replace(" ",""))
        timestamp = float(updstr[i+l:i2].replace(",",'').replace(" ",""))

    def __str__(self):
        return "'index': {index},\
            'miner': {miner},\
            'timestamp': {timestamp},\
            'basemodel': {basemodel},\
            'accuracy': {accuracy},\
            'updates': {updates},\
            'proof': {proof},\
            'previous_hash': {previous_hash},\
            'updates_size': {updates_size}".format(
                index = self.index,
                miner = self.miner,
                basemodel = self.basemodel,
                accuracy = self.accuracy,
                timestamp = self.timestamp,
                updates = str([str(x) for x in self.updates]),
                proof = self.proof,
                previous_hash = self.previous_hash,
                updates_size = str(len(self.updates))
            )#.encode()



class Blockchain(object):
    def __init__(self,miner_id,base_model=None,gen=False):
        super(Blockchain,self).__init__()
        self.miner_id = miner_id
        self.chain = []
        self.current_updates = dict()
        # Create the genesis block
        if gen:
            genesis = self.make_block(base_model=base_model,previous_hash=1)
            self.store_block(genesis)
        self.nodes = set()

    def register_node(self,address):
        if address[:4] != "http":
            address = "http://"+address
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        print("Registered node",address)
        print(self.nodes)

    def make_block(self,previous_hash=None,base_model=None):
        accuracy = 0
        basemodel = None
        if previous_hash==None:
            previous_hash = self.hash(self.last_block)
        if base_model!=None:
            accuracy = base_model['accuracy']
            basemodel = base_model['model']
        elif len(self.current_updates)>0:
            accuracy,basemodel = compute_global_model(self.current_updates)
        block = Block(
            miner = self.miner_id,
            index = len(self.chain)+1,
            basemodel = basemodel,
            accuracy = accuracy,
            updates = self.current_updates,
            proof = random.randint(0,100000000),
            previous_hash = previous_hash
            )
        return block

    def store_block(self,block):
        self.chain.append(block)
        self.current_updates = dict()
        return block

    def new_update(self,client,baseindex,update,datasize,computing_time):
        self.current_updates[client] = Update(
            client = client,
            baseindex = baseindex,
            update = update,
            datasize = datasize,
            computing_time = computing_time
            )
        return self.last_block.index+1

    @staticmethod
    def hash(block):
        return hashlib.sha256(str(block)).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]


    def proof_of_work(self,stop_event):
        block = self.make_block()
        stopped = False
        while self.valid_proof(str(block)) is False:
            if stop_event.is_set():
                stopped = True
                break
            block.proof += 1
            if block.proof%1000==0:
                print("mining",block.proof)
        if stopped==False:
            self.store_block(block)
        return block,stopped

    @staticmethod
    def valid_proof(block_data):
        guess_hash = hashlib.sha256(block_data).hexdigest()
        k = "00000000"
        return guess_hash[:len(k)] == k


    def valid_chain(self,chain):
        last_block = chain[0]
        curren_index = 1
        while curren_index<len(chain):
            block = chain[curren_index]
            if block.previous_hash != self.hash(last_block):
                return False
            if not self.valid_proof(str(block)):
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
                chain = []
                for b in response.json()['chain']:
                    chain.append(Block.from_string(b))
                if length>max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False
