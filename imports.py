from gevent import monkey
import logging
from logging.handlers import RotatingFileHandler
import sys 
import platform
from Features.secret import generate_secret_key
import random
import json
import pickle
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from keras.models import load_model
from flask import Flask, render_template, request, jsonify, session, send_file
from fuzzysearch import find_near_matches
from difflib import SequenceMatcher
import tensorflow as tf
import tensorflow_datasets as tfds
from transformers import BertTokenizer, TFBertForSequenceClassification, AdamWeightDecay
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Input, Embedding, LSTM, Dense, concatenate, Bidirectional, Attention, Flatten, Concatenate
from keras.optimizers import Adam, SGD
import gensim.models
from gensim.models import Word2Vec
from concurrent.futures import ThreadPoolExecutor
from fuzzywuzzy import process, fuzz
import spacy
from flask_cors import CORS
from Features.sentiments import  analyze_sentiment
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from nltk.sentiment import SentimentIntensityAnalyzer
import hashlib
from cryptography.fernet import Fernet
from flask_sslify import SSLify
import os
import ssl
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet
import spacy
from spacy import displacy
import re
from spacy.matcher import Matcher
import csv
import csv
from datetime import datetime
