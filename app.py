from imports import *

# Initialize Flask app
app = Flask(__name__)
# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Generate a secret key for symmetric encryption (replace with proper key management)
symmetric_key = Fernet.generate_key()
cipher_suite = Fernet(symmetric_key)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Set a secret key for authentication
app.config['SECRET_KEY'] = generate_secret_key()

# Initialize conversation history to keep track of user-bot interactions
conversation_history = []
recipe_data = []

# Paths to data and models
input_data_path = 'data/input'
output_data_path = 'data/output'

# Load intents data from the input directory
intents_data_path = os.path.join(input_data_path, 'intents.json')
intents = json.loads(open(intents_data_path).read())

# Load the model from the output directory
model_path = os.path.join(output_data_path, 'Attention', 'attention.model')
# Assuming load_model is implemented elsewhere
model = load_model(model_path)

# Load words and classes from the output directory
words_path = os.path.join(output_data_path, 'Attention', 'words.pkl')
classes_path = os.path.join(output_data_path, 'Attention', 'classes.pkl')
words = pickle.load(open(words_path, 'rb'))
classes = pickle.load(open(classes_path, 'rb'))

# Initialize WordNet Lemmatizer for text processing
lemmatizer = WordNetLemmatizer()
# Reuse objects whenever possible
stop_words = set(stopwords.words('english'))
# Convert recipe names to a set for faster membership checks
recipe_names_set = set(recipe['recipe_name'].lower() for recipe in intents['recipes'])

# API endpoint to serve files from the input directory
@app.route('/api/get_input_file/<filename>', methods=['GET'])
def get_input_file(filename):
    file_path = os.path.join(input_data_path, filename)
    return send_file(file_path, as_attachment=True)

# API endpoint to serve files from the output directory
@app.route('/api/get_output_file/<path:filename>', methods=['GET'])
def get_output_file(filename):
    file_path = os.path.join(output_data_path, filename)
    return send_file(file_path, as_attachment=True)

# Read file contents once during initialization
intents_data_path = os.path.join(input_data_path, 'intents.json')
intents = json.loads(open(intents_data_path).read())

# Update the preprocess_input function to include POS tags
def preprocess_input(input_text):
    input_text = input_text.lower()
    doc = nlp(input_text)
    # Extract POS tags
    pos_tags = [token.pos_ for token in doc]
    # Extract entities
    entities = [ent.text for ent in doc.ents]
    # Tokenize the input text
    tokens = word_tokenize(input_text)
    # Remove stopwords (optional)
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatize tokens
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # Add recognized entities and POS tags to the lemmatized tokens
    tokens.extend(entities)
    tokens.extend(pos_tags)
    # Reconstruct the preprocessed text
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text

# Functions to clear up noisy data from dataset
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

# The 'bag_of_words' function converts a sentence into a binary vector representation,
# where each element corresponds to a word in a predefined vocabulary. If a word from
# the vocabulary is present in the input sentence, the corresponding element in the
# binary vector is set to 1; otherwise, it remains 0.
# Update the bag_of_words function to include POS features
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    pos_tags = pos_tags_in_sentence(sentence)  # New function to extract POS tags
    sentence_words.extend(pos_tags)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# New function to extract POS tags from a sentence
def pos_tags_in_sentence(sentence):
    doc = nlp(sentence.lower())
    pos_tags = [token.pos_ for token in doc]
    print(f"POS Tags: {pos_tags}")  # Add this line for debugging
    return pos_tags

def format_recipe(recipe):
    recipe_name = recipe.get('recipe_name', '')
    ingredients = recipe.get('ingredients', [])
    methods = recipe.get('methods', [])
    formatted_recipe_details = [f"Recipe: {recipe_name}", "Ingredients:"]
    formatted_recipe_details.extend(ingredients)
    formatted_recipe_details.append("Methods:")
    formatted_recipe_details.extend(methods)
    return formatted_recipe_details


def extract_recipe_name(user_message):
    user_message = user_message.lower()
    best_match, similarity = process.extractOne(user_message, recipe_names_set, scorer=fuzz.ratio)
    # Define a similarity threshold (adjust as needed)
    similarity_threshold = 80  # Adjust as needed (percentage similarity)
    if similarity >= similarity_threshold:
        print(f"Found recipe name ({similarity}% match): {best_match}")
        return best_match
    else:
        print("No exact match found, using fallback.")  # Add this line
        return None


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_closest_recipe_names(user_message):
    user_message = user_message.lower()  # Convert to lowercase for case-insensitive matching
    # Define a similarity threshold (adjust as needed)
    similarity_threshold = 0.5
    best_matches = []
    for recipe_name in recipe_names_set:
        similarity = similar(user_message, recipe_name)
        if similarity >= similarity_threshold:
            best_matches.append(recipe_name)
    # Check for known synonyms/aliases and map to canonical form
    synonym_dict = {
        "biriyni": "biriyani",
        # Add more entries for other common variations
    }
    for synonym, canonical in synonym_dict.items():
        if synonym in user_message:
            best_matches.append(canonical)  # Add canonical form
    return best_matches


def get_recipe_details(recipe_name):
    if recipe_name in recipe_data:
        ingredients = recipe_data[recipe_name]["ingredients"]
        methods = recipe_data[recipe_name]["methods"]
        recipe_details = {
            "text": f"Here's the recipe for {recipe_name}:\n\nIngredients:\n" + "\n".join(
                ingredients) + "\n\nMethods:\n" + "\n".join(methods),
            "is_recipe": True
        }
        print("Recipe details:", recipe_details)  # Add this line
        return recipe_details
    else:
        return {"text": "I'm sorry, I couldn't find the recipe you're looking for.", "is_recipe": False}


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    # Calculate the dynamic threshold as a percentage of the maximum confidence score
    threshold_percentage = 80  # Adjust as needed
    dynamic_threshold = max(res) * (threshold_percentage / 100)
    print(f"Dynamic Threshold: {dynamic_threshold}")
    results = [[i, r] for i, r in enumerate(res) if r > dynamic_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if not results:
        # If no intent is above the threshold, use a fallback response
        return_list.append({'intent': 'fallback', 'probability': '1'})
        print("Fallback triggered due to no intent above threshold.")  # Add this line for debugging
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json, user_message):
    # Extract the recipe name from the user's message
    recipe_name = extract_recipe_name(user_message)
    if recipe_name:
        # Check if the recipe name matches any recipe in the dataset
        for recipe in intents_json['recipes']:
            if recipe['recipe_name'].lower() == recipe_name.lower():
                return format_recipe(recipe)
        response = "I'm sorry, I couldn't find the recipe you're looking for."
    else:
        # Continue with the existing response logic based on predicted intents
        tag = intents_list[0]['intent']
        pos_tags = pos_tags_in_sentence(user_message)  # Extract POS tags
        user_message_with_pos = user_message + ' ' + ' '.join(pos_tags)
        ints = predict_class(user_message_with_pos)
        # Extracted POS features
        extracted_pos_features = ', '.join(pos_tags)
        print(f"Extracted POS features: {extracted_pos_features}")  # Add this line for debugging
        # Check if the top predicted intent is related to recipe details
        if tag == 'recipe_details':
            recipe_name = extract_recipe_name(user_message)
            bot_message = get_recipe_details(recipe_name)
        else:
            # Continue with the existing response logic based on predicted intents
            list_of_intents = intents_json['intents']
            response = None
            for i in list_of_intents:
                if i['tag'] == tag:
                    response = random.choice(i['responses'])
                    break
            # If no matching intent found, use a fallback response
            if not response:
                response = "Hi there, how can I help?"
            print("Using fallback response.")  # Add this line for debugging
            bot_message = response
        # Log the predicted intent and response
        app.logger.info(f"Predicted Intent: {tag}, Response: {bot_message}")  # Add this line
    return bot_message 

@socketio.on('signal')
def handle_signal(data):
    # Encrypt the message before broadcasting
    encrypted_message = cipher_suite.encrypt(data['message'].encode())
    emit('signal', {'message': encrypted_message}, broadcast=True)
    # Log encryption information
    app.logger.info(f"Encrypted message: {data['message']}")

def handle_message():
    user_message = request.json.get('message')
    # Encrypt the user message for secure communication
    encrypted_user_message = cipher_suite.encrypt(user_message.encode())
    # Broadcast the encrypted user message to all connected clients
    send('message from server', f"Bot: You said - '{encrypted_user_message.decode()}'", broadcast=True)
    # Decrypt the message for application logic (not shown here)
    decrypted_user_message = cipher_suite.decrypt(encrypted_user_message).decode()
    # Log encryption information
    app.logger.info(f"Decrypted message: {decrypted_user_message}")
    return {'message': 'Message received successfully!'}

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    # Sentiment analysis
    sentiment = analyze_sentiment(user_message)
    print(f"Sentiment: {sentiment}")
    # Extract POS tags for debugging
    pos_tags = pos_tags_in_sentence(user_message)
    print(f"POS Tags: {pos_tags}")  # Add this line for debugging
    conversation_history.append({'user': user_message, 'bot': None})
    keyword_for_recipe = 'recipe'
    if keyword_for_recipe in user_message.lower():
        suggestions = get_closest_recipe_names(user_message)
        if suggestions:
            suggestion_message = "Did you mean: "
            if len(suggestions) == 2:
                suggestion_message += f"{suggestions[0]} or {suggestions[1]}"
            else:
                suggestion_message += ', '.join(suggestions)
            bot_message = suggestion_message
        else:
            bot_message = "I couldn't find any recipe suggestions."
    else:
        ints = predict_class(user_message)
        tag = ints[0]['intent']
        if tag == 'recipe_details':
            recipe_name = extract_recipe_name(user_message)
            bot_message = get_recipe_details(recipe_name)
        else:
            bot_message = get_response(ints, intents, user_message)
            # Extract POS tags again for debugging within the get_response function
            pos_tags = pos_tags_in_sentence(user_message)
            print(f"POS Tags within get_response: {pos_tags}")  # Add this line for debugging
    conversation_history[-1]['bot'] = bot_message
    return jsonify({'message': bot_message, 'history': conversation_history, 'sentiment': sentiment})


# Main entry point
if __name__ == '__main__':
    # Run the app with the secret key
    Important_message = "Important: Application started with secret key."
    print(Important_message)  # Print important message

    socketio.run(app, debug=True, host='0.0.0.0', port=1000, use_reloader=False) 
    