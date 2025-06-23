# Mayabati - Your Personal AI Chef  -  **Developed by Biswadeb Mukherjee (Lead Developer, ParseSphere Innovations)**
```
Mayabati/
|
├── Backend/                          # Backend Directory
│   ├── data/                         # Data processing directory
│   │   ├── input/                    # Input data for training models
│   │   │   ├── gram.json
│   │   │   └── intents.json
│   │   └── output/                   # Model outputs
│   │       ├── Transformer Based Model/
│   │       │   ├── Rasika.model
│   │       │   ├── classes.pkl
│   │       │   └── words.pkl
│   │       └── gram.model
│   ├── trainer/                      # Model training modules
│   │   ├── __init__.py
│   │   ├── trainer.py
│   │   └── gram.py
│   ├── app.py                        # Flask App entry point
│   ├── imports.py                    # Import all backend libraries
│   ├── secret.py                     # Encryption algorithms
│   ├── decision.py                   # Bot decision-making logic
│   └── requirements.txt              # Backend dependencies
|
├── Frontend/                         # Advanced Frontend Directory
│   ├── public/                       # Public static files
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── images/
│   │       ├── user.jpg
│   │       └── bot.jpg
│   ├── src/                          # Frontend source code
│   │   ├── assets/                   # Images, icons, fonts
│   │   │   ├── images/
│   │   │   └── icons/
│   │   ├── components/               # Reusable UI components
│   │   │   ├── Chat/
│   │   │   │   ├── Chat.jsx
│   │   │   │   ├── Chat.module.css
│   │   │   │   └── Chat.test.jsx
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   └── UI/                   # Buttons, Loaders, Cards, Modals
│   │   ├── layouts/                  # Page layouts with header/sidebar
│   │   ├── pages/                    # Route-based pages
│   │   │   ├── Home/
│   │   │   ├── About/
│   │   │   └── NotFound/
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── context/                  # Context API Providers
│   │   ├── services/                 # API service handlers
│   │   ├── utils/                    # Utility functions
│   │   ├── router/                   # Router configuration
│   │   │   └── index.jsx
│   │   ├── store/                    # State management setup (Redux/Zustand)
│   │   ├── i18n/                     # Internationalization (optional)
│   │   ├── App.jsx
│   │   ├── main.jsx                  # Main entry point (Vite)
│   │   └── styles/                   # Global styles and variables
│   │       ├── variables.css
│   │       └── globals.css
│   ├── .env                          # Environment configurations
│   ├── .gitignore
│   ├── package.json                  # Frontend dependencies
│   ├── package-lock.json
│   ├── vite.config.js                # Vite configuration (if used)
│   └── README.md                     # Frontend documentation
|
├── README.txt                        # Main Project README
├── Project.md                        # 📖 Project Directory Documentation (This file)
└── License.md                        # License details
```
