from imports import *

# Load the dataset from intents.json
with open('data/input/intents.json', 'r') as file:
    data = json.load(file)

# Extract recipe names and patterns
recipe_names = [recipe["recipe_name"] for recipe in data["recipes"]]
patterns = [pattern for recipe in data["recipes"] for pattern in recipe["patterns"]]

# Create pairs of recipes for training the siamese network
pairs = [(recipe_name, pattern) for recipe_name in recipe_names for pattern in patterns]

# Create labels (1 for positive pairs, 0 for negative pairs)
labels = [1 if pair[0] == pair[1] else 0 for pair in pairs]

# Split the data into training and validation sets
pairs_train, pairs_val, labels_train, labels_val = train_test_split(pairs, labels, test_size=0.2, random_state=42)

# Extract text from tuples
recipes_train, patterns_train = zip(*pairs_train)
recipes_val, patterns_val = zip(*pairs_val)

# Tokenize recipe names and patterns
tokenizer = Tokenizer()
tokenizer.fit_on_texts(recipe_names + patterns)

# Convert text data to sequences
recipes_train_seq = tokenizer.texts_to_sequences(recipes_train)
patterns_train_seq = tokenizer.texts_to_sequences(patterns_train)
recipes_val_seq = tokenizer.texts_to_sequences(recipes_val)
patterns_val_seq = tokenizer.texts_to_sequences(patterns_val)

# Pad sequences for a consistent input shape
recipes_train_pad = pad_sequences(recipes_train_seq)
patterns_train_pad = pad_sequences(patterns_train_seq)
recipes_val_pad = pad_sequences(recipes_val_seq)
patterns_val_pad = pad_sequences(patterns_val_seq)

# Define and compile the siamese network
embedding_dim = 50
recipe_input = Input(shape=(None,))
pattern_input = Input(shape=(None,))

embedding_layer = Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=embedding_dim)

embedded_recipe = embedding_layer(recipe_input)
embedded_pattern = embedding_layer(pattern_input)

lstm_layer = LSTM(50)

lstm_recipe = lstm_layer(embedded_recipe)
lstm_pattern = lstm_layer(embedded_pattern)

concatenated = concatenate([lstm_recipe, lstm_pattern])
output = Dense(1, activation='sigmoid')(concatenated)

siamese_model = Model(inputs=[recipe_input, pattern_input], outputs=output)
siamese_model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])

# Convert labels to numpy array
labels_train_np = np.array(labels_train)
labels_val_np = np.array(labels_val)

# Train the model
siamese_model.fit(
    x=[recipes_train_pad, patterns_train_pad],
    y=labels_train_np,
    epochs=20,
    batch_size=32,
    validation_data=([recipes_val_pad, patterns_val_pad], labels_val_np)
)

# Save the trained model
siamese_model.save('data/output/decision.model')