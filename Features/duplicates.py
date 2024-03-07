# Open the text file containing names
with open("./Features/unique_diets.txt", "r") as file:
    # Read all lines from the file
    lines = file.readlines()

# Strip whitespace and newline characters from each line and store them in a list
names = [line.strip() for line in lines]

# Initialize an empty dictionary to store occurrences of each name
occurrences = {}

# Iterate through the list of names and count occurrences of each name
for name in names:
    if name in occurrences:
        occurrences[name] += 1
    else:
        occurrences[name] = 1

# Print duplicates
print("Duplicates:")
for name, count in occurrences.items():
    if count > 1:
        print(name)
