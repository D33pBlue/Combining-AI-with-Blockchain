import warnings; warnings.simplefilter('ignore')
import tensorflow as tf
import pickle
from nn import *
from blockchain import *
from uuid import uuid4
import requests

class Client:
    def __init__(self,miner,dataset):
        self.id = str(uuid4()).replace('-','')
        self.miner = miner
        self.dataset = self.load_dataset(dataset)

    def get_last_base_model(self):
        response = requests.get('http://{node}/chain'.format(node=self.miner))
        if response.status_code == 200:
            length = response.json()['length']
            chain = []
            for b in response.json()['chain']:
                chain.append(Block.from_string(b))
            return chain[-1].basemodel

    def get_miner_status(self):
        response = requests.get('http://{node}/status'.format(node=self.miner))
        if response.status_code == 200:
            return response.json()['status']

    def load_dataset(self,name):
        return []

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-m', '--miner', default='127.0.0.1:5000', help='Address of miner')
    parser.add_argument('-d', '--dataset', default='data/mnist.d', help='Path to dataset')
    args = parser.parse_args()
    client = Client(args.miner,args.dataset)
    print(client.get_miner_status())
