import json

# Load the existing dataset from the given JSON
with open('data/input/intents.json', 'r', encoding='utf-8') as file:
    recipes_data = json.load(file)

# Extract "recipe_name" and "ingredients" for each recipe
extracted_data = []
for recipe in recipes_data['recipes']:
    recipe_info = {
        'recipe_name': recipe['recipe_name'],
        'ingredients': recipe['ingredients']
    }
    extracted_data.append(recipe_info)

# Save the extracted data to a new JSON file
output_file_path = 'data/input/decision.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(extracted_data, output_file, ensure_ascii=False, indent=2)

print(f"Extraction complete. Data saved to '{output_file_path}'.")
