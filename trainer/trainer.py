import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Dropout, Embedding, Bidirectional, LSTM, Input, Attention, Flatten, Concatenate  # Import Concatenate
from keras.optimizers import SGD
import gensim.models

lemmatizer = WordNetLemmatizer()

# Load pre-trained Word2Vec model
w2v_model = gensim.models.Word2Vec.load("data/output/gram.model")

# Define your classes and documents based on your dataset
# For example, assuming you have an intents.json file as in your initial code:
intents = json.loads(open('data/input/intents.json').read())

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('data/output/Attention/words.pkl', 'wb'))
pickle.dump(classes, open('data/output/Attention/classes.pkl', 'wb'))

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

random.shuffle(training)

# Separate train_x and train_y
train_x = np.array([item[0] for item in training])
train_y = np.array([item[1] for item in training])

# Attention Mechanism
input_layer = Input(shape=(len(train_x[0]),))
embedding_layer = Embedding(input_dim=len(words), output_dim=100)(input_layer)
# First Attention Mechanism
lstm_layer = Bidirectional(LSTM(130, return_sequences=True))(embedding_layer)
attention1 = Attention()([lstm_layer, lstm_layer])
attention1 = Flatten()(attention1)
# Second Attention Mechanism
lstm_layer2 = Bidirectional(LSTM(130, return_sequences=True))(lstm_layer)
attention2 = Attention()([lstm_layer2, lstm_layer2])
attention2 = Flatten()(attention2)
# Concatenate both attention outputs
concatenated_attention = Concatenate()([attention1, attention2])
output_layer = Dense(len(train_y[0]), activation='softmax')(concatenated_attention)

model = Model(inputs=[input_layer], outputs=[output_layer])

# Define the optimizer with learning rate (lr) instead of decay
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

model.fit(train_x, train_y, epochs=500, batch_size=200)
model.save('data/output/Attention/Rasika.model')
print("Done")