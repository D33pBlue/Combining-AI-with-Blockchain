import warnings; warnings.simplefilter('ignore')
import tensorflow as tf
import pickle
from nn import *
from blockchain import *
from uuid import uuid4
import requests
import data.extractor as dataext

class Client:
    def __init__(self,miner,dataset):
        self.id = str(uuid4()).replace('-','')
        self.miner = miner
        self.dataset = self.load_dataset(dataset)

    def get_last_block(self):
        response = requests.get('http://{node}/chain'.format(node=self.miner))
        if response.status_code == 200:
            # length = response.json()['length']
            # chain = []
            # for b in response.json()['chain']:
                # chain.append(Block.from_string(b))
            # return chain[-1]
            return Block.from_string(response.json()['chain'][-1])

    def get_miner_status(self):
        response = requests.get('http://{node}/status'.format(node=self.miner))
        if response.status_code == 200:
            return response.json()['status']

    def load_dataset(self,name):
        return dataext.load_data(name)

    def update_model(self,steps):
        reset()
        last_block = self.get_last_block()
        t = time.time()
        worker = NNWorker(self.dataset['train_img'],
            self.dataset['train_lab'],
            self.dataset['test_img'],
            self.dataset['test_lab'],
            len(self.dataset['train_img']),
            self.id,
            steps)
        worker.build(last_block.basemodel)
        worker.train()
        update = worker.get_model()
        accuracy = worker.evaluate()
        worker.close()
        return update,accuracy,time.time()-t,last_block.index

    def send_update(self,update,cmp_time,baseindex):
        requests.post('http://{node}/transactions/new'.format(node=self.miner),
            json={
                'client': self.id,
                'baseindex': baseindex,
                'update': codecs.encode(pickle.dumps(sorted(update.items())), "base64").decode(),
                'datasize': len(self.dataset['train_img']),
                'computing_time': cmp_time
            })

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-m', '--miner', default='127.0.0.1:5000', help='Address of miner')
    parser.add_argument('-d', '--dataset', default='data/mnist.d', help='Path to dataset')
    args = parser.parse_args()
    client = Client(args.miner,args.dataset)
    print("--------------")
    print(client.id," Dataset info:")
    dataext.show_dataset_info(client.dataset)
    print("--------------")
    update,accuracy,cmp_time,baseindex = client.update_model(10)
    print("Accuracy local update:",accuracy)
    client.send_update(update,cmp_time,baseindex)
