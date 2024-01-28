Mayabati - Your Personal AI Chef [Made by Biswadeb Mukherjee (Lead Developer of ParseSphere Innovations.)]
|
├── Backend/                           # Backend directory
│   ├── data/                          # Directory for backend data processing
│   │   ├── input/                     # Input data directory
│   │   │   ├── gram.json              # Input data for training using Word2vec model
│   │   │   └── intents.json           # Input data for training using custom dataset
│   │   └── output/                    # Output data directory
│   │       ├── Transformer Based Model/  # Directory for Transformer Based Model output
│   │       │   ├── Rasika.model       # Output model for Transformer Based Model
│   │       │   ├── classes.pkl        # Output classes for Transformer Based Model
│   │       │   └── words.pkl          # Output words for Transformer Based Model
│   │       └── gram.model             # Output model for Gram model
│   ├── trainer/                       # Directory for training-related modules
│   │   ├── __init__.py                # Empty file to make 'trainer' a Python package
│   │   ├── trainer.py                 # Main trainer module
│   │   └── gram.py                    # Module for Gram model
│   ├── app.py                         # Main Flask App
│   ├── imports.py                     # File to import all libraries
│   ├── secret.py                      # Encryption algorithm for website security
│   ├── decision.py                    # Module for bot decision-making
│   └── requirements.txt               # File listing Python libraries used in the project
|
├── Frontend/                          # Frontend directory
│   ├── public/                        # Public assets directory
│   │   ├── index.html                 # Main HTML template
│   │   └── images/                    # Directory for images
│   │       ├── user.jpg               # User image
│   │       └── bot.jpg                # Bot image
│   ├── src/                           # Source code directory
│   │   ├── components/                # Directory for React components
│   │   │   ├── Chat.js                # Chat component
│   │   │   └── ...                    # Other components
│   │   ├── App.js                     # Main App component
│   │   ├── index.js                   # Entry point for React app
│   │   └── styles/                    # Directory for CSS styles or SCSS
│   │       └── style.css              # CSS styles file
│   ├── .gitignore                     # File containing names of files/folders ignored by git
│   ├── package.json                   # npm package configuration
│   ├── package-lock.json              # npm package lock file
│   └── README.md                      # Frontend README
├── README.txt                         # Project README
├── Project.md                         # Project Directory Structure documentation
└── License.md                         # License instructions for the project