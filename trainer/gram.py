from imports import *

# Load the JSON file containing the corpus
with open('gram.json', 'r') as json_file:
    corpus = json.load(json_file)

# Tokenize and preprocess the corpus
lemmatizer = WordNetLemmatizer()
tokenized_corpus = [word_tokenize(sentence.lower()) for sentence in corpus]
tokenized_corpus = [[lemmatizer.lemmatize(word) for word in sentence if word.isalnum()] for sentence in tokenized_corpus]

# Train Word2Vec embeddings
w2v_model = Word2Vec(tokenized_corpus, vector_size=100, window=5, min_count=1, sg=0)  # Adjust parameters as needed
w2v_model.save("gram.model")
print("Done")