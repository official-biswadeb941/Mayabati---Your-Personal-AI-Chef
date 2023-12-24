import logging
from logging.handlers import RotatingFileHandler
import sys 
import os
import platform
from secret import generate_secret_key
import random                  # For generating random responses
import json                    # For handling JSON data
import pickle                  # For serializing and deserializing Python objects
import numpy as np             # For numerical operations
import nltk                    # Natural Language Toolkit for text processing
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize  # Lemmatization tool from NLTK
from keras.models import load_model     # Loading a deep learning model using Keras
from flask import Flask, render_template, request, jsonify  # Flask web framework for building a web application
from fuzzysearch import find_near_matches
from difflib import SequenceMatcher
import tensorflow as tf
import tensorflow_datasets as tfds
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import AdamWeightDecay
import json
import numpy as np
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Input, Embedding, LSTM, Dense, concatenate
from keras.models import Model
from keras.optimizers import Adam
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
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from fuzzysearch import find_near_matches
from flask import Flask, request, jsonify, render_template
from flask.logging import default_handler
from logging.handlers import RotatingFileHandler
import logging
import sys
import platform
import json
import pickle
from difflib import SequenceMatcher
import random
from nltk import word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
import numpy as np
from keras.models import load_model
from concurrent.futures import ThreadPoolExecutor
from fuzzywuzzy import process
from fuzzywuzzy import fuzz



