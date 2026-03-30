import os
from typing import Dict, List

# Load environment variables (assumes python-dotenv or environment setup)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Red Flag Categories
RED_FLAGS: Dict[str, List[str]] = {
    "Sensationalism": [
        "unbelievable",
        "shocking",
        "bombshell",
        "jaw-dropping",
        "mind-blowing",
        "must-see",
        "destroy",
        "obliterate",
    ],
    "Bias": [
        "corrupt",
        "fake news",
        "agenda",
        "mainstream media",
        "sheeple",
        "woke",
        "draconian",
    ],
    "Clickbait": [
        "you won't believe",
        "secret revealed",
        "what happens next",
        "this one weird trick",
        "number 3 will shock you",
        "doctors hate",
    ]
}
