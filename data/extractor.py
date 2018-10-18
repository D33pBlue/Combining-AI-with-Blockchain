import warnings; warnings.simplefilter('ignore')

import tensorflow as tf
import numpy as np
import pickle

def get_mnist():
    from tensorflow.examples.tutorials.mnist import input_data
    mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
    dataset = dict()
    dataset["train_img"] = mnist.train.images
    dataset["train_lab"] = mnist.train.labels
    dataset["test_img"] = mnist.test.images
    dataset["test_lab"] = mnist.test.labels
    return dataset

def save_data(dataset,name="mnist.d"):
    with open(name,"wb") as f:
        pickle.dump(dataset,f)

def load_data(name="mnist.d"):
    with open(name,"rb") as f:
        return pickle.load(f)

def show_dataset_info(dataset):
    for k in dataset.keys():
        print(k,dataset[k].shape)

def split_dataset(dataset,k):
    datasets = []
    s = len(dataset["train_img"])//k
    for i in range(k):
        d = dict()
        d["test_img"] = dataset["test_img"][:]
        d["test_lab"] = dataset["test_lab"][:]
        d["train_img"] = dataset["train_img"][i*s:(i+1)*s]
        d["train_lab"] = dataset["train_lab"][i*s:(i+1)*s]
        datasets.append(d)
    return datasets


if __name__ == '__main__':
    save_data(get_mnist())
    dataset = load_data()
    show_dataset_info(dataset)
    for j,d in enumerate(split_dataset(dataset,10)):
        save_data(d,"d"+str(j)+".d")
        dk = load_data("d"+str(j)+".d")
        show_dataset_info(dk)
        print()
