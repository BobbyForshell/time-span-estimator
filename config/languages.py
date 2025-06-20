# Language configuration
LANGUAGES = {
    "en": "English",
    "sv": "Svenska"
}

# Import all translation files
from translations.en import ENGLISH_TEXTS
from translations.sv import SWEDISH_TEXTS

TEXTS = {
    "en": ENGLISH_TEXTS,
    "sv": SWEDISH_TEXTS
}

def get_text(key, language=None):
    """Get text in the specified language"""
    if language is None:
        language = "en"  # Default to English
    return TEXTS[language].get(key, key) 