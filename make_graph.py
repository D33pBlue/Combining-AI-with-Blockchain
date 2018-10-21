from matplotlib import pyplot as plt
from client import Client
from nn import *


def get_centralized_accuracy(epc):
    reset()
    dataset = None
    with open("data/mnist.d",'rb') as f:
        dataset = pickle.load(f)
    worker = NNWorker(dataset["train_img"],
        dataset["train_lab"],
        dataset["test_img"],
        dataset["test_lab"],
        0,
        "base0",
        epc)
    cntz_acc = worker.centralized_accuracy()
    worker.close()
    return cntz_acc


def plot_graph(chain,epc):
    cntz_acc = get_centralized_accuracy(epc)
    plt.plot(cntz_acc['epoch'],cntz_acc['accuracy'],label="Centralized")
    epoch = []
    accuracy = []
    for i in range(len(chain)):
        epoch.append(int(chain[i]['index']))
        accuracy.append(float(chain[i]['accuracy']))
    plt.plot(epoch,accuracy,label="Blockchained")
    plt.title("Accuracy in epochs comparison (3 clients)")
    plt.legend()
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.show()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-m', '--miner', default='127.0.0.1:5000', help='Address of miner')
    parser.add_argument('-l', '--ulimit', default=10, type=int, help='number of updates stored in one block')
    args = parser.parse_args()
    client = Client(args.miner,None)
    chain = client.get_chain()
    plot_graph(chain,args.ulimit)
