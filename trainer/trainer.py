import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import gensim.models
import tensorflow as tf
from keras.layers import Layer, Input, Embedding, Dense, LSTM, Bidirectional, Attention, Flatten, Concatenate
from keras.models import Model
from keras.optimizers import SGD

# Load intents from a JSON file
intents = json.loads(open('intents.json').read())

# Extract intent data for further processing (assuming intents is a list)
words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

nltk.download('punkt')  # Download the punkt tokenizer data
nltk.download('wordnet')  # Download the WordNet data

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Load pre-trained Word2Vec model
w2v_model = gensim.models.Word2Vec.load("gram.model")

# Preprocess words, classes, and documents
lemmatizer = WordNetLemmatizer()

# Lemmatize and preprocess words, removing ignore_letters
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(set(words))

# Sort classes
classes = sorted(set(classes))

# Create training data
training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

# Shuffle the training data
random.shuffle(training)

# Separate train_x and train_y
train_x = np.array([item[0] for item in training])
train_y = np.array([item[1] for item in training])

# Attention Mechanism
input_layer = Input(shape=(len(train_x[0]),))
embedding_layer = Embedding(input_dim=len(words), output_dim=100)(input_layer)
lstm_layer = Bidirectional(LSTM(150, return_sequences=True))(embedding_layer)
attention1 = Attention()([lstm_layer, lstm_layer])
attention1 = Flatten()(attention1)
lstm_layer2 = Bidirectional(LSTM(150, return_sequences=True))(lstm_layer)
attention2 = Attention()([lstm_layer2, lstm_layer2])
attention2 = Flatten()(attention2)
concatenated_attention = Concatenate()([attention1, attention2])

# Define a Neural Turing Machine (NTM) controller layer
class NTMController(Layer):
    def __init__(self, output_dim, **kwargs):
        super(NTMController, self).__init__(**kwargs)
        self.output_dim = output_dim

    def build(self, input_shape):
        # Define controller parameters (weights and biases)
        self.controller_weights = self.add_weight(shape=(input_shape[-1], self.output_dim),
                                                  initializer='uniform',
                                                  trainable=True)
        self.controller_bias = self.add_weight(shape=(self.output_dim,),
                                               initializer='uniform',
                                               trainable=True)
        super(NTMController, self).build(input_shape)

    def call(self, x):
        # Implement controller logic here
        controller_output = tf.matmul(x, self.controller_weights) + self.controller_bias
        return controller_output

# Define a Neural Turing Machine (NTM) memory layer
class NTMMemory(Layer):
    def __init__(self, memory_size, memory_dim, **kwargs):
        super(NTMMemory, self).__init__(**kwargs)
        self.memory_size = memory_size
        self.memory_dim = memory_dim

    def build(self, input_shape):
        # Define memory parameters (memory matrix and addressing mechanisms)
        self.memory_matrix = self.add_weight(shape=(self.memory_size, self.memory_dim),
                                             initializer='zeros',
                                             trainable=True,  # Ensure it's trainable
                                             name='memory_matrix')
        super(NTMMemory, self).build(input_shape)

    def call(self, x):
        # Implement memory read and write operations here
        # Example: Memory read operation (read_head_weight is a weight matrix for read head)
        read_head_weight = self.add_weight(shape=(self.memory_size,),
                                           initializer='uniform',
                                           trainable=True,
                                           name='read_head_weight')
        read_weights = tf.nn.softmax(read_head_weight, axis=-1)

        # Reshape the read_weights to rank-2 tensor with shape (batch_size, memory_size)
        read_weights = tf.expand_dims(read_weights, axis=0)
        read_data = tf.matmul(read_weights, self.memory_matrix, transpose_b=True)

        # Example: Memory write operation (write_head_weight is a weight matrix for write head)
        write_head_weight = self.add_weight(shape=(self.memory_size,),
                                            initializer='uniform',
                                            trainable=True,
                                            name='write_head_weight')
        write_weights = tf.nn.softmax(write_head_weight, axis=-1)
        write_data = tf.matmul(tf.expand_dims(write_weights, axis=-1), tf.expand_dims(x, axis=1))

        # Combine read and write data to get the final memory data
        memory_data = read_data + write_data

        return memory_data

# Add NTM Controller and Memory
controller_output = NTMController(output_dim=128)(concatenated_attention)
memory_data = NTMMemory(memory_size=128, memory_dim=128)(controller_output)

# Define the number of classes
num_classes = len(classes)

# Define the output layer with the correct number of units and softmax activation
output_layer = Dense(num_classes, activation='softmax')(concatenated_attention)

model = Model(inputs=[input_layer], outputs=[output_layer])

# Define the optimizer with learning rate (lr) instead of decay
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train the model
model.fit(train_x, train_y, epochs=6000, batch_size=25)

model_save_path = 'attention.model'
model.save(model_save_path)
print("Done")