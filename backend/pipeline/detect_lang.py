import re
from typing import Optional
import langdetect

LANG_MAP = {
    "hi": "Hindi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "kn": "Kannada",
    "ml": "Malayalam",
    "en": "English"
}

# List of common Hinglish/romanized Hindi words for language detection
HINGLISH_WORDS = {
    "mujhe", "bukhar", "dard", "hai", "sar", "pet", "khansi", "ulti", "dawai",
    "tabiyat", "kharab", "bimari", "ilaj", "asar", "taklif", "ladka", "ladki",
    "accha", "theek", "nahi", "haan", "kaise", "kya", "kab", "kahan"
}

# Romanized lists for other Indian languages
GUJARATI_WORDS = {"che", "mane", "taav", "su", "kem", "majama", "saru", "kharab", "dukhe"}
TAMIL_WORDS = {"irukku", "enaku", "vanthuruchu", "eppadi", "illa", "vali", "jurama"}
TELUGU_WORDS = {"undi", "naaku", "vachindi", "ela", "ledu", "noppi", "jwaram"}
MARATHI_WORDS = {"aahe", "mala", "zala", "kasa", "nahi", "dukhi", "taap"}

def is_hinglish(text: str) -> bool:
    """
    Checks if the text is Hinglish (romanized Hindi) by matching HINGLISH_WORDS.
    """
    words = re.findall(r'\b[a-z]+\b', text.lower())
    matching_words = {w for w in words if w in HINGLISH_WORDS}
    return len(matching_words) >= 2

def detect_romanized_language(text: str) -> Optional[str]:
    """
    Checks the text against each word list (case-insensitive, word boundary match)
    Returns the matching language code (gu, ta, te, mr) if 2+ words match
    Returns None if no clear match
    """
    words = re.findall(r'\b[a-z]+\b', text.lower())
    word_set = set(words)
    
    if len(word_set & GUJARATI_WORDS) >= 2:
        return "gu"
    if len(word_set & TAMIL_WORDS) >= 2:
        return "ta"
    if len(word_set & TELUGU_WORDS) >= 2:
        return "te"
    if len(word_set & MARATHI_WORDS) >= 2:
        return "mr"
    
    return None

def detect_language(text: str) -> str:
    """
    Detects the language of the input text.
    Returns ISO 639-1 language code (e.g. 'en', 'hi', 'ta').
    If detection fails or language not in LANG_MAP, return "en"
    """
    if not text or not text.strip():
        return "en"
    
    # 1. First check is_hinglish() (existing Hindi check) — return "hi" if true
    if is_hinglish(text):
        return "hi"
        
    # 2. Then check detect_romanized_language() — return its result if not None
    roman_lang = detect_romanized_language(text)
    if roman_lang is not None:
        return roman_lang
        
    # 3. Then check Devanagari/other Indic unicode script ranges
    # Indic unicode ranges:
    # Devanagari: \u0900-\u097f (Hindi, Marathi)
    # Bengali: \u0980-\u09ff
    # Gujarati: \u0a80-\u0aff
    # Tamil: \u0b80-\u0bff
    # Telugu: \u0c00-\u0c7f
    # Kannada: \u0c80-\u0cff
    # Malayalam: \u0d00-\u0d7f
    indic_ranges = {
        "gu": r"[\u0a80-\u0aff]",
        "ta": r"[\u0b80-\u0bff]",
        "te": r"[\u0c00-\u0c7f]",
        "bn": r"[\u0980-\u09ff]",
        "kn": r"[\u0c80-\u0cff]",
        "ml": r"[\u0d00-\u0d7f]",
        "devanagari": r"[\u0900-\u097f]"
    }
    
    for lang_code, pattern in indic_ranges.items():
        if re.search(pattern, text):
            if lang_code == "devanagari":
                try:
                    detected = langdetect.detect(text)
                    if detected in ("hi", "mr"):
                        return detected
                except Exception:
                    pass
                return "hi"  # Default fallback for Devanagari script
            return lang_code
            
    # 4. Then fall back to existing langdetect logic
    try:
        lang = langdetect.detect(text)
        if lang in LANG_MAP:
            return lang
    except Exception:
        pass
        
    # 5. Final fallback "en" if nothing matches
    return "en"


