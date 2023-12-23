from imports import *

# Initialize Flask app
app = Flask(__name__)

# Set a secret key for authentication
app.config['SECRET_KEY'] = generate_secret_key()

# Configure Flask app to use file-based logging only
log_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

# Disable console logging for Flask
app.logger.removeHandler(default_handler := logging.StreamHandler(sys.stdout))

# Redirect all messages to the log file
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable Flask default logger, preventing messages from being printed to the console
app.logger.disabled = True

# Initialize conversation history to keep track of user-bot interactions
conversation_history = []
recipe_data = []

# Load model and data once during initialization
model = load_model('data/output/attention.model')
intents = json.loads(open('data/input/intents.json').read())
words = pickle.load(open('data/output/words.pkl', 'rb'))
classes = pickle.load(open('data/output/classes.pkl', 'rb'))

# Initialize WordNet Lemmatizer for text processing
lemmatizer = WordNetLemmatizer()

# Reuse objects whenever possible
stop_words = set(stopwords.words('english'))

# Convert recipe names to a set for faster membership checks
recipe_names_set = set(recipe['recipe_name'].lower() for recipe in intents['recipes'])

# Read file contents once during initialization
intents_data = open('data/input/intents.json').read()
intents = json.loads(intents_data)


def preprocess_input(input_text):
    # Convert to lowercase
    input_text = input_text.lower()
    # Tokenize the input text
    tokens = word_tokenize(input_text)
    # Remove stopwords (optional)
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatize tokens
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # Reconstruct the preprocessed text
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text


#Functions to clear up noisy data from dataset
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


# The 'bag_of_words' function converts a sentence into a binary vector representation,
# where each element corresponds to a word in a predefined vocabulary. If a word from
# the vocabulary is present in the input sentence, the corresponding element in the
# binary vector is set to 1; otherwise, it remains 0.
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


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
    for intent in intents['recipes']:
        if 'patterns' in intent:
            for pattern in intent['patterns']:
                if pattern.lower() in user_message:
                    print("Found recipe name:", intent['recipe_name'])  # Add this line
                    return intent['recipe_name']
    return None  # Return None if no recipe name is found


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
    ERROR_THRESHOLD = 0.4  # Adjust the threshold as needed
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if not results:
        # If no intent is above the threshold, use a fallback response
        return_list.append({'intent': 'fallback', 'probability': '1'})
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json, user_message):
    # Extract the recipe name from the user's message
    recipe_name = extract_recipe_name(user_message)
    if recipe_name:
        print("Recipe name extracted:", recipe_name)  # Add this line
        # Check if the recipe name matches any recipe in the dataset
        for recipe in intents_json['recipes']:
            if recipe['recipe_name'].lower() == recipe_name.lower():
                # Return the recipe details as a response
                print("Found matching recipe in dataset.")  # Add this line
                return format_recipe(recipe)
        # If no matching recipe found, return a message
        response = "I'm sorry, I couldn't find the recipe you're looking for."
        print("No matching recipe found in the dataset.")  # Add this line
    else:
        # Continue with the existing response logic based on predicted intents
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        response = None
        for i in list_of_intents:
            if i['tag'] == tag:
                response = random.choice(i['responses'])
                break
        # If no matching intent found, use a fallback response
        if not response:
            response = "Hi there, how can I help?"
        print("Using fallback response.")  # Add this line
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
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

    conversation_history[-1]['bot'] = bot_message
    return jsonify({'message': bot_message, 'history': conversation_history})

# Main entry point
if __name__ == '__main__':
    # Print system information at startup
    system_info = f"System: {platform.system()} {platform.release()} {platform.machine()}"
    app.logger.info(system_info)  # Log system information

    # Run the app with the secret key
    important_message = "Important: Application started with secret key."
    app.logger.info(important_message)  # Log important message
    print(important_message)  # Print important message

    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)
