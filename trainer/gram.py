from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec
import json

with open('data/input/gram.json', 'r') as json_file:
    corpus = json.load(json_file)

lemmatizer = WordNetLemmatizer()
tokenized_corpus = [word_tokenize(sentence.lower()) for sentence in corpus]
tokenized_corpus = [[lemmatizer.lemmatize(word) for word in sentence if word.isalnum()] for sentence in tokenized_corpus]

w2v_model = Word2Vec(tokenized_corpus, vector_size=100, window=5, min_count=1, sg=0) 
w2v_model.save("data/output/gram.model")
print("Done")
