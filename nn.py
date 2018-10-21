import warnings; warnings.simplefilter('ignore')
import tensorflow as tf
import numpy as np
import pickle

def reset():
    tf.reset_default_graph()

class NNWorker:
    def __init__(self,X=None,Y=None,tX=None,tY=None,size=0,id="nn0",steps=10):
        # Parameters
        self.id = id
        # Data
        self.train_x = X
        self.train_y = Y
        self.test_x = tX
        self.test_y = tY
        self.size = size
        # Network Parameters
        self.learning_rate = 0.1
        self.num_steps = steps
        self.n_hidden_1 = 256 # 1st layer number of neurons
        self.n_hidden_2 = 256 # 2nd layer number of neurons
        self.num_input = 784 # MNIST data input (img shape: 28*28)
        self.num_classes = 10 # MNIST total classes (0-9 digits)
        self.sess = tf.Session()

    def build(self,base):
        # tf Graph input
        self.X = tf.placeholder("float", [None, self.num_input])
        self.Y = tf.placeholder("float", [None, self.num_classes])
        # Store layers weight & bias
        self.weights = {
            'h1': tf.Variable(base['h1'],name="h1"),
            'h2': tf.Variable(base['h2'],name="h2"),
            'out': tf.Variable(base['ho'],name="ho")
        }
        self.biases = {
            'b1': tf.Variable(base['b1'],name="b1"),
            'b2': tf.Variable(base['b2'],name="b2"),
            'out': tf.Variable(base['bo'],name="bo")
        }
        # Construct model
        # Hidden fully connected layer with 256 neurons
        self.layer_1 = tf.add(tf.matmul(self.X, self.weights['h1']), self.biases['b1'])
        # Hidden fully connected layer with 256 neurons
        self.layer_2 = tf.add(tf.matmul(self.layer_1, self.weights['h2']),self.biases['b2'])
        # Output fully connected layer with a neuron for each class
        self.out_layer = tf.matmul(self.layer_2, self.weights['out'])+self.biases['out']
        self.logits = self.out_layer
        # For validation
        self.correct_pred = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.Y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
        # Initialize the variables (i.e. assign their default value)
        self.init = tf.global_variables_initializer()
        # Run the initializer
        self.sess.run(self.init)

    def build_base(self):
        # tf Graph input
        self.X = tf.placeholder("float", [None, self.num_input])
        self.Y = tf.placeholder("float", [None, self.num_classes])
        # Store layers weight & bias
        self.weights = {
            'h1': tf.Variable(tf.random_normal([self.num_input, self.n_hidden_1]),name="h1"),
            'h2': tf.Variable(tf.random_normal([self.n_hidden_1, self.n_hidden_2]),name="h2"),
            'out': tf.Variable(tf.random_normal([self.n_hidden_2, self.num_classes]),name="ho")
        }
        self.biases = {
            'b1': tf.Variable(tf.random_normal([self.n_hidden_1]),name="b1"),
            'b2': tf.Variable(tf.random_normal([self.n_hidden_2]),name="b2"),
            'out': tf.Variable(tf.random_normal([self.num_classes]),name="bo")
        }
        # Construct model
        # Hidden fully connected layer with 256 neurons
        self.layer_1 = tf.add(tf.matmul(self.X, self.weights['h1']), self.biases['b1'])
        # Hidden fully connected layer with 256 neurons
        self.layer_2 = tf.add(tf.matmul(self.layer_1, self.weights['h2']),self.biases['b2'])
        # Output fully connected layer with a neuron for each class
        self.out_layer = tf.matmul(self.layer_2, self.weights['out'])+self.biases['out']
        self.logits = self.out_layer
        # For validation
        self.correct_pred = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.Y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
        # Initialize the variables (i.e. assign their default value)
        self.init = tf.global_variables_initializer()
        # Run the initializer
        self.sess.run(self.init)

    def train(self):
        # Define loss and optimizer
        self.loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
            logits=self.logits, labels=self.Y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        self.train_op = self.optimizer.minimize(self.loss_op)
        # Run the initializer
        self.init = tf.global_variables_initializer()
        self.sess.run(self.init)
        # Start training
        for step in range(1, self.num_steps+1):
            # Run optimization op (backprop)
            self.sess.run(self.train_op, feed_dict={self.X: self.train_x, self.Y: self.train_y})
            # Calculate batch loss and accuracy
            # loss, acc = self.sess.run([self.loss_op, self.accuracy],
            #     feed_dict={self.X: self.train_x,self.Y: self.train_y})
        #     print("Step " + str(step) + ", Minibatch Loss= " + \
        #         "{:.4f}".format(loss) + ", Training Accuracy= " + \
        #         "{:.3f}".format(acc))
        # print("Optimization Finished!")


    def centralized_accuracy(self):
        cntz_acc = dict()
        cntz_acc['epoch'] = []
        cntz_acc['accuracy'] = []
        self.build_base()
        # Define loss and optimizer
        self.loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
            logits=self.logits, labels=self.Y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        self.train_op = self.optimizer.minimize(self.loss_op)
        # Run the initializer
        self.init = tf.global_variables_initializer()
        self.sess.run(self.init)
        # Start training
        for step in range(self.num_steps):
            # Run optimization op (backprop)
            self.sess.run(self.train_op, feed_dict={self.X: self.train_x, self.Y: self.train_y})
            cntz_acc['epoch'].append(step)
            acc = self.evaluate()
            cntz_acc['accuracy'].append(acc)
            print("epoch",step,"accuracy",acc)
        return cntz_acc


    def evaluate(self):
        # Calculate accuracy for MNIST test images
        return self.sess.run(self.accuracy, feed_dict={self.X: self.test_x,self.Y:self.test_y})

    def load_model(self,name):
        with open("models/"+name+".m","rb") as f:
            return pickle.load(f)

    def save_model(self,name):
        varsk = {tf.trainable_variables()[i].name[:2]:tf.trainable_variables()[i].eval(self.sess) for i in range(len(tf.trainable_variables()))}
        varsk["size"] = self.size
        with open("models/"+name+".m","wb") as f:
            pickle.dump(varsk,f)

    def get_model(self):
        varsk = {tf.trainable_variables()[i].name[:2]:tf.trainable_variables()[i].eval(self.sess) for i in range(len(tf.trainable_variables()))}
        varsk["size"] = self.size
        return varsk

    def close(self):
        self.sess.close()
