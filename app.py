
from imports import *

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

symmetric_key = Fernet.generate_key()
cipher_suite = Fernet(symmetric_key)

nlp = spacy.load("en_core_web_sm")

app.config['SECRET_KEY'] = generate_secret_key()

conversation_history = []
recipe_data = []

input_data_path = 'data/input'
output_data_path = 'data/output'

intents_data_path = os.path.join(input_data_path, 'intents.json')
intents = json.loads(open(intents_data_path).read())

model_path = os.path.join(output_data_path, 'Attention', 'attention.model')
model = load_model(model_path)


words_path = os.path.join(output_data_path, 'Attention', 'words.pkl')
classes_path = os.path.join(output_data_path, 'Attention', 'classes.pkl')
words = pickle.load(open(words_path, 'rb'))
classes = pickle.load(open(classes_path, 'rb'))

lemmatizer = WordNetLemmatizer()

stop_words = set(stopwords.words('english'))
recipe_names_set = set(recipe['recipe_name'].lower() for recipe in intents['recipes'])

@app.route('/api/get_input_file/<filename>', methods=['GET'])
def get_input_file(filename):
    file_path = os.path.join(input_data_path, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/api/get_output_file/<path:filename>', methods=['GET'])
def get_output_file(filename):
    file_path = os.path.join(output_data_path, filename)
    return send_file(file_path, as_attachment=True)

intents_data_path = os.path.join(input_data_path, 'intents.json')
intents = json.loads(open(intents_data_path).read())

def preprocess_input(input_text):
    input_text = input_text.lower()
    doc = nlp(input_text)
    
    pos_tags = [token.pos_ for token in doc]
    entities = [ent.text for ent in doc.ents]
    tokens = word_tokenize(input_text)
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    tokens.extend(entities)
    tokens.extend(pos_tags)
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    pos_tags = pos_tags_in_sentence(sentence)  
    sentence_words.extend(pos_tags)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def pos_tags_in_sentence(sentence):
    doc = nlp(sentence.lower())
    pos_tags = [token.pos_ for token in doc]
    print(f"POS Tags: {pos_tags}")  
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
    similarity_threshold = 80 
    if similarity >= similarity_threshold:
        print(f"Found recipe name ({similarity}% match): {best_match}")
        return best_match
    else:
        print("No exact match found, using fallback.") 
        return None


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_closest_recipe_names(user_message):
    user_message = user_message.lower() 
    similarity_threshold = 0.5
    best_matches = []
    for recipe_name in recipe_names_set:
        similarity = similar(user_message, recipe_name)
        if similarity >= similarity_threshold:
            best_matches.append(recipe_name)
    synonym_dict = {
        "biriyni": "biriyani",
    }
    for synonym, canonical in synonym_dict.items():
        if synonym in user_message:
            best_matches.append(canonical) 
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
        print("Recipe details:", recipe_details)  
        return recipe_details
    else:
        return {"text": "I'm sorry, I couldn't find the recipe you're looking for.", "is_recipe": False}


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    threshold_percentage = 80 
    dynamic_threshold = max(res) * (threshold_percentage / 100)
    print(f"Dynamic Threshold: {dynamic_threshold}")
    results = [[i, r] for i, r in enumerate(res) if r > dynamic_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if not results:
        return_list.append({'intent': 'fallback', 'probability': '1'})
        print("Fallback triggered due to no intent above threshold.")
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json, user_message):
    recipe_name = extract_recipe_name(user_message)
    if recipe_name:
        for recipe in intents_json['recipes']:
            if recipe['recipe_name'].lower() == recipe_name.lower():
                return format_recipe(recipe)
        response = "I'm sorry, I couldn't find the recipe you're looking for."
    else:
        tag = intents_list[0]['intent']
        pos_tags = pos_tags_in_sentence(user_message)
        user_message_with_pos = user_message + ' ' + ' '.join(pos_tags)
        ints = predict_class(user_message_with_pos)
        extracted_pos_features = ', '.join(pos_tags)
        print(f"Extracted POS features: {extracted_pos_features}") 
        if tag == 'recipe_details':
            recipe_name = extract_recipe_name(user_message)
            bot_message = get_recipe_details(recipe_name)
        else:
            list_of_intents = intents_json['intents']
            response = None
            for i in list_of_intents:
                if i['tag'] == tag:
                    response = random.choice(i['responses'])
                    break
            if not response:
                response = "Hi there, how can I help?"
            print("Using fallback response.")
            bot_message = response
        app.logger.info(f"Predicted Intent: {tag}, Response: {bot_message}")

@socketio.on('signal')
def handle_signal(data):
    encrypted_message = cipher_suite.encrypt(data['message'].encode())
    emit('signal', {'message': encrypted_message}, broadcast=True)
    app.logger.info(f"Encrypted message: {data['message']}")

def handle_message():
    user_message = request.json.get('message')
    encrypted_user_message = cipher_suite.encrypt(user_message.encode())
    send('message from server', f"Bot: You said - '{encrypted_user_message.decode()}'", broadcast=True)
    decrypted_user_message = cipher_suite.decrypt(encrypted_user_message).decode()
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
    sentiment = analyze_sentiment(user_message)
    print(f"Sentiment: {sentiment}")
    pos_tags = pos_tags_in_sentence(user_message)
    print(f"POS Tags: {pos_tags}") 
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
            pos_tags = pos_tags_in_sentence(user_message)
            print(f"POS Tags within get_response: {pos_tags}") 
    conversation_history[-1]['bot'] = bot_message
    return jsonify({'message': bot_message, 'history': conversation_history, 'sentiment': sentiment})


if __name__ == '__main__':
    Important_message = "Important: Application started with secret key."
    print(Important_message) 
    socketio.run(app, debug=True, host='0.0.0.0', port=1000, use_reloader=False) 
    