Mayabati - Your Personal AI Chef [Made by Biswadeb Mukherjee (Lead Developer of ParseSphere Innovations.)]
│
├── data/
│   ├── input/
│   │   ├── gram.json                  # Input data for training using Word2vec model.
│   │   └── intents.json               # Input data for training using custom dataset.
│   └── output/
│       ├── Transformer Based Model/
│       │   ├── Rasika.model               # Output model.
│       │   ├── classes.pkl                # Output classes.
│       │   └── words.pkl                  # Output words.
│       └── gram.model                    # Output model.
│
├── static/
│   ├── css/
│   │   ├── style.css                  # CSS styles.
│   └── images/
│       ├── user.jpg                   # User image.
│       └── bot.jpg                    # Bot image.
│
├── templates/
│   ├── index.html                     # HTML template.
│
├── trainer/
│   ├── __init__.py                   # Empty file to make 'trainer' a Python package.
│   ├── trainer.py                     # Trainer module.
│   └── gram.py                        # Gram module.
│
├── .gitignore                         # Contain names of the files or folders to be ignored by git.
├── app.py                             # Main Flask App.
├── imports.py                         # To import all libraries.
├── secret.py                          # Encryption algorithm which provides security for overall website.
├── decision.py                        # So that the bot can think and take hardcore decisions just like humans.
├── License.md                         # Contain the license instructions about this project.
├── Project.md                         # Contain the Project Directory Structure.
├── README.md                          # Full Project Explanation for GitHub.
└── requirements.txt                   # Python libraries used in this project.
