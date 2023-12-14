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
