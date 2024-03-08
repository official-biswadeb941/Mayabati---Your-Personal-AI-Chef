from imports import *

app = Flask(__name__)
redis_client = redis.StrictRedis(host='0.0.0.0', port=705, db=0)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://0.0.0.0:700/0'})

symmetric_key = Fernet.generate_key()
cipher_suite = Fernet(symmetric_key)

nlp = spacy.load("en_core_web_sm")
recognizer = sr.Recognizer()

app.config['SECRET_KEY'] = os.urandom(24)
conversation_history = []

num_folds = 5  
threshold_percentage = 80
input_data_path = os.path.join('data', 'input')
output_data_path = os.path.join('data', 'output')

intents_data_path = os.path.join(input_data_path, 'intents.json')
with open(intents_data_path, 'r') as intents_file:
    intents = json.load(intents_file)

model_path = os.path.join(output_data_path, 'Attention', 'Rasika.model')
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
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/get_output_file/<path:filename>', methods=['GET'])
def get_output_file(filename):
    file_path = os.path.join(output_data_path, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


def recognize_speech(request):
    try:
        if 'speech' in request.files:
            speech_file = request.files['speech']
            with sr.AudioFile(speech_file) as audio_file:
                audio_data = recognizer.record(audio_file)
            user_message = recognizer.recognize_google(audio_data)
            return user_message
    except IOError as e:
        app.logger.error(f"io_error in speech recognition: {e}")
        return "io_error occurred in speech recognition."
    except FileNotFoundError as e:
        app.logger.error(f"file_not_found_error in speech recognition: {e}")
        return "file_not_found_error occurred in speech recognition."
    except sr.UnknownValueError as e:
        app.logger.error(f"unknown_value_error in speech recognition: {e}")
        return "unknown_value_error occurred in speech recognition."
    except sr.RequestError as e:
        app.logger.error(f"request_error in speech recognition: {e}")
        return "request_error occurred in speech recognition."
    except Exception as e:
        app.logger.error(f"error in speech recognition: {e}")
        return "error occurred in speech recognition."


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
    preprocessed_sentence = preprocess_input(sentence)
    sentence_words = nltk.word_tokenize(preprocessed_sentence)
    pos_tags = pos_tags_in_sentence(preprocessed_sentence)
    sentence_words.extend(pos_tags)
    bag = [0] * len(words)
    for w in sentence_words:
        if w in words:
            bag[words.index(w)] = 1
    return np.array(bag)

 
def pos_tags_in_sentence(sentence):
    doc = nlp(sentence.lower())
    pos_tags = [token.pos_ for token in doc]
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
    if len(a) != len(b):
        return 0  
    return SequenceMatcher(None, a, b).ratio()

def get_closest_recipe_names(user_message):
    user_message = user_message.lower()
    average_length = sum(len(name) for name in recipe_names_set) / len(recipe_names_set)
    similarity_threshold = 0.5 * (len(user_message) / average_length)
    best_matches = [recipe_name for recipe_name in recipe_names_set
                    if similar(user_message, recipe_name) >= similarity_threshold]
    synonym_dict = {"biriyni": "biriyani"}
    for synonym, canonical in synonym_dict.items():
        if synonym in user_message:
            best_matches.append(canonical)
    return best_matches

def get_recipe_details(recipe_name):
    lowercase_recipe_name = recipe_name.lower()  #
    if lowercase_recipe_name in (recipe['recipe_name'].lower() for recipe in intents['recipes']):
        recipe = next(recipe for recipe in intents['recipes'] if recipe['recipe_name'].lower() == lowercase_recipe_name)
        ingredients = recipe.get('ingredients', [])
        methods = recipe.get('methods', [])
        recipe_details = {
            "text": f"Here's the recipe for {recipe['recipe_name']}:\n\nIngredients:\n" + "\n".join(ingredients) + 
                    "\n\nMethods:\n" + "\n".join(methods),
            "is_recipe": True
        }
        print("Recipe details:", recipe_details)
        return recipe_details
    else:
        return {"text": "I'm sorry, I couldn't find the recipe you're looking for.", "is_recipe": False}

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    threshold = np.mean(res) + np.std(res)
    print(f"Dynamic Threshold: {threshold}")
    results = [[i, r] for i, r in enumerate(res) if r > threshold]
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
    pos_tags = pos_tags_in_sentence(user_message)
    if recipe_name:
        user_message_with_pos = user_message + ' ' + ' '.join(pos_tags)
        if recipe_name:
            recipe = next((r for r in intents_json['recipes'] if r['recipe_name'].lower() == recipe_name.lower()), None)
            if recipe:
                return format_recipe(recipe)
            response = "I'm sorry, I couldn't find the recipe you're looking for."
    else:
        tag = intents_list[0]['intent']
        user_message_with_pos = user_message + ' ' + ' '.join(pos_tags)
        ints = predict_class(user_message_with_pos)
        extracted_pos_features = ', '.join(pos_tags)
        print(f"Extracted POS features: {extracted_pos_features}")
        if tag == 'recipe_details':
            recipe_name = extract_recipe_name(user_message)
            bot_message = get_recipe_details(recipe_name)
        else:
            list_of_intents = intents_json['intents']
            response = next((i['responses'][0] for i in list_of_intents if i['tag'] == tag), "Hi there, how can I help?")
            print("Using fallback response.")
            bot_message = response
        app.logger.info(f"Predicted Intent: {tag}, Response: {bot_message}")
    return bot_message

@app.route('/')
def index():
    return render_template('Chatbot.html')

def conversation_logs(user_message, bot_message, sentiment, response_time):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_history.append({
        'timestamp': timestamp,
        'user': user_message,
        'bot': bot_message,
        'sentiment': sentiment,
        'response_time': response_time  # Include response time in the conversation history
    })
    csv_file_path = os.path.join(output_data_path, 'Conversation', 'History.csv')
    fieldnames = ['Date', 'Time', 'User', 'Bot', 'Sentiment', 'Response Time']  # Include 'Response Time' in fieldnames
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for entry in conversation_history[-1:]:
            date, time = entry['timestamp'].split()
            writer.writerow({
                'Date': date,
                'Time': time,
                'User': entry['user'],
                'Bot': entry['bot'],
                'Sentiment': entry['sentiment'],
                'Response Time': entry['response_time']  # Write response time to CSV
            })
    return conversation_history


 
@app.route('/chat', methods=['POST'])
def chat():
    try:
        start_time = time.time()  # Capture the start time
        user_message = request.json.get('message')
        sentiment = analyze_sentiment(user_message)
        print(f"Sentiment: {sentiment}")
        pos_tags = pos_tags_in_sentence(user_message)
        print(f"POS Tags: {pos_tags}")
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
        end_time = time.time()  # Capture the end time
        response_time = end_time - start_time  # Calculate the response time  
        conversation_logs(user_message, bot_message, sentiment, response_time)
        print(f"Bot Response Time: {response_time} seconds")  # Print the response time
        return {'message': bot_message, 'history': conversation_history, 'sentiment': sentiment}
    except Exception as e:
        app.logger.error(f"error in chat endpoint: {e}")
        return {'message': 'Error occurred in processing the request.'}
    
if __name__ == '__main__':
    important_message = "Important: Application started with a securely with secret key."
    print(important_message)
    app.run(debug=True, host='0.0.0.0', port=700)
