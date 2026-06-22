from deep_translator import GoogleTranslator

def to_english(text: str, source_lang: str) -> str:
    """
    Translates text to English using GoogleTranslator.
    If source_lang is "en", return text unchanged.
    If translation fails, return original text unchanged.
    """
    if source_lang == "en":
        return text
    try:
        return GoogleTranslator(source=source_lang, target="en").translate(text)
    except Exception:
        return text

def from_english(text: str, target_lang: str) -> str:
    """
    Translates text from English to target_lang using GoogleTranslator.
    If target_lang is "en", return text unchanged.
    If translation fails, return original text unchanged.
    """
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except Exception:
        return text

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translates text from source language to target language.
    """
    if source_lang == target_lang:
        return text
    if source_lang == "en":
        return from_english(text, target_lang)
    if target_lang == "en":
        return to_english(text, source_lang)
    
    # Translate to English first, then to target
    en_text = to_english(text, source_lang)
    return from_english(en_text, target_lang)


