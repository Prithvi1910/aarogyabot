import os
import sys

# Ensure backend directory is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import detect_language, to_english, from_english, translate_text, classify_urgency, triage_symptoms

def main():
    print("=== TESTING LANGUAGE DETECTION ===")
    tests_detect = [
        ("Hello, how are you today?", "en"),
        ("नमस्ते, आप कैसे हैं?", "hi"),
        ("મને તમારી મદદની જરૂર છે", "gu"),  # Gujarati
        ("मला ताप आला आहे", "mr"),        # Marathi
        ("எனக்கு உதவி தேவை", "ta"),         # Tamil
        ("నాకు జ్వరం వచ్చింది", "te"),      # Telugu
        ("আমার জ্বর হয়েছে", "bn"),          # Bengali
        ("ನನಗೆ ಸಹಾಯ ಬೇಕು", "kn"),         # Kannada
        ("എനിക്ക് സുഖമില്ല", "ml"),         # Malayalam
        ("12345", "en"),                  # Punctuation/numbers (should fallback to en)
        ("", "en"),                       # Empty string (should fallback to en)
        # Hinglish test cases
        ("mujhe bukhar hai", "hi"),       # "mujhe", "bukhar", "hai" (3 words) -> hi
        ("pet kharab hai", "hi"),         # "pet", "kharab", "hai" (3 words) -> hi
        ("mujhe headache hai", "hi"),     # "mujhe", "hai" (2 words) -> hi
        ("my pet dog is sick", "en"),     # "pet" (1 word) -> en (should not trigger)
        ("sar dard medicine", "hi"),      # "sar", "dard" (2 words) -> hi
        ("I have a fever", "en"),         # 0 Hinglish words -> en
        # Romanized Gujarati test cases
        ("mane taav che", "gu"),          # "mane", "taav", "che" (3 words) -> gu
        ("kem majama che", "gu"),         # "kem", "majama", "che" (3 words) -> gu
        ("kem che", "gu"),                # "kem", "che" (2 words) -> gu
        ("kem", "en"),                    # 1 word -> en
        # Romanized Tamil test cases
        ("enaku jurama irukku", "ta"),    # "enaku", "jurama", "irukku" (3 words) -> ta
        ("vali illa", "ta"),              # "vali", "illa" (2 words) -> ta
        ("vali", "en"),                   # 1 word -> en
        # Romanized Telugu test cases
        ("naaku jwaram undi", "te"),      # "naaku", "jwaram", "undi" (3 words) -> te
        ("ela undi", "te"),               # "ela", "undi" (2 words) -> te
        ("noppi ledu", "te"),             # "noppi", "ledu" (2 words) -> te
        # Romanized Marathi test cases
        ("mala taap aahe", "mr"),         # "mala", "taap", "aahe" (3 words) -> mr
        ("kasa aahe", "mr"),              # "kasa", "aahe" (2 words) -> mr
        ("kasa", "en")                    # 1 word -> en
    ]
    for text, expected in tests_detect:
        res = detect_language(text)
        print(f"Text: {repr(text)} -> Detected: {res} (Expected: {expected})")

    print("\n=== TESTING TRANSLATION ===")
    print("Testing 'to_english' (en -> en):")
    print(to_english("Hello", "en"))
    
    print("Testing 'from_english' (en -> en):")
    print(from_english("Hello", "en"))
    
    print("Testing translation to English (Hindi -> English) via API:")
    translated_to = to_english("नमस्ते", "hi")
    print(f"'नमस्ते' -> {repr(translated_to)}")
    
    print("Testing translation from English (English -> Hindi) via API:")
    translated_from = from_english("Hello", "hi")
    print(f"'Hello' -> {repr(translated_from)}")

    print("Testing translate_text (Hindi -> Tamil) via API:")
    translated_full = translate_text("नमस्ते", "hi", "ta")
    print(f"'नमस्ते' (hi) -> {repr(translated_full)} (ta)")

    print("\n=== TESTING TRIAGE & URGENCY CLASSIFICATION ===")
    test_triage_texts = [
        ("I have severe chest pain and heart attack symptoms.", "EMERGENCY"),
        ("I have a mild cough and fever since yesterday.", "VISIT_PHC"),
        ("Just feeling a bit tired, no other symptoms.", "SELF_CARE")
    ]
    for text, expected_level in test_triage_texts:
        urgency = classify_urgency(text)
        symptoms_info = triage_symptoms(text)
        print(f"Text: {repr(text)}")
        print(f"  Urgency: {urgency}")
        print(f"  Triage Symptoms: {symptoms_info}")

if __name__ == "__main__":
    main()
