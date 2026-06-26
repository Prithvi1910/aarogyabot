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
    "en": "English",
    "pa": "Punjabi",
    "ur": "Urdu",
    "or": "Odia",
    "as": "Assamese"
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
PUNJABI_WORDS = {"menu", "tenu", "kida", "kiddan", "ki haal", "sat sri akal", "tussi", "sanu", "ohna", "kithey", "kithe", "labna", "akhna", "dasna", "hanji", "paji", "karo", "veere", "kiwe", "pra", "changa", "wadhia", "sada", "tuhada"}
URDU_WORDS = {"aapko", "unhe", "humein", "zaroor", "bilkul", "shayad", "warna", "lekin", "phir", "abhi", "matlab", "tabiyat", "sehat", "ilaj", "dawa", "mareez"}
ODIA_WORDS = {"mora", "tuma", "achi", "jiba", "kara", "kahuchi", "dekhuchi", "sunuchi", "asthu", "thanda", "garma", "peta", "mathu"}
ASSAMESE_WORDS = {"mur", "tumar", "ase", "nai", "jai", "kora", "bhal", "osodh", "pikora", "jwor", "gaa", "mur gaa", "lagise", "pain lagise"}

def count_matches(text: str, word_set: set) -> int:
    """Counts how many words/phrases from the word_set are present in the text."""
    text_lower = text.lower()
    count = 0
    for word in word_set:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            count += 1
    return count

def detect_language(text: str) -> str:
    """
    Detects the language of the input text.
    Returns ISO 639-1 language code (e.g. 'en', 'hi', 'ta').
    If detection fails or language not in LANG_MAP, return "en"
    """
    if not text or not text.strip():
        return "en"
    
    # 1. Check for Romanized Indian languages first by counting matches
    matches = {
        "as": count_matches(text, ASSAMESE_WORDS),
        "or": count_matches(text, ODIA_WORDS),
        "pa": count_matches(text, PUNJABI_WORDS),
        "ur": count_matches(text, URDU_WORDS),
        "gu": count_matches(text, GUJARATI_WORDS),
        "ta": count_matches(text, TAMIL_WORDS),
        "te": count_matches(text, TELUGU_WORDS),
        "mr": count_matches(text, MARATHI_WORDS),
        "hi": count_matches(text, HINGLISH_WORDS)
    }
    
    # Find the language with the maximum matches
    max_lang = max(matches, key=matches.get)
    max_count = matches[max_lang]
    
    # If we found at least 1 match, we return the language with the most matches.
    # For Hinglish ('hi'), require at least 2 matches to avoid false positives with common words,
    # unless it's the only one that matched. Actually, let's just return if max_count >= 1 for regional,
    # and >= 2 for Hinglish. Wait, if Hinglish has 1 and no one else has matches, maybe just return hi?
    # Let's say if max_count >= 1, we trust it for non-Hindi. For Hindi, let's require >= 2 matches or we fall through.
    if max_count > 0:
        if max_lang == "hi" and max_count < 2:
            pass # Too few matches for Hinglish, fall through to other methods
        else:
            return max_lang
            
    # 2. Check Devanagari/other Indic unicode script ranges
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
            
    # 3. Fall back to existing langdetect logic
    try:
        lang = langdetect.detect(text)
        if lang in LANG_MAP:
            return lang
    except Exception:
        pass
        
    # 4. Final fallback "en" if nothing matches
    return "en"


