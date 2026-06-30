from typing import Dict, Any

EMERGENCY_KEYWORDS = [
    "chest pain",
    "heart attack",
    "unconscious",
    "not breathing",
    "can't breathe",
    "cant breathe",
    "difficulty breathing",
    "trouble breathing",
    "blue lips",
    "seizure",
    "fits",
    "convulsion",
    "stroke",
    "severe bleeding",
    "heavy bleeding",
    "bleeding that won't stop",
    "vomiting blood",
    "coughing blood",
    "poisoning",
    "pesticide",
    "snake bite",
    "snakebite",
    "snake bit",
    "bitten by a snake",
    "drowning",
    "electric shock",
    "severe burn",
    "heat stroke",
    "fear of water",
    "choking"
]

# High-risk conditions that warrant a PHC visit even when mentioned alone.
HIGH_RISK_PHC_KEYWORDS = [
    "dog bite",
    "dog bit",
    "animal bite",
    "animal bit",
    "monkey bite",
    "monkey bit",
    "cat bite",
    "cat bit",
    "bitten by a dog",
    "bitten by an animal",
    "rabies",
    "deep wound",
    "jaundice",
    "yellow eyes",
    "blood in stool",
    "blood in urine",
    "night blindness",
    "burn",
    "fracture",
    "broken bone"
]

PHC_KEYWORDS = [
    "fever",
    "cough",
    "diarrhea",
    "diarrhoea",
    "vomiting",
    "rash",
    "itching",
    "infection",
    "pain",
    "weakness",
    "swelling",
    "diabetes",
    "blood pressure",
    "malaria",
    "dengue",
    "worms",
    "anaemia",
    "anemia",
    "boil",
    "wound",
    "scabies",
    "ringworm"
]

SYMPTOM_COMBINATIONS = {
    "malaria": ["fever", "chills", "sweating", "headache"],
    "dengue": ["fever", "pain behind the eyes", "joint pain", "rash"],
    "tuberculosis": ["cough", "weight loss", "night sweats", "fever"],
    "typhoid": ["fever", "headache", "stomach pain", "diarrhea"],
    "chikungunya": ["fever", "joint pain", "joint swelling", "rash"],
    "cholera": ["watery stools", "vomiting", "muscle cramps", "thirst"],
    "hepatitis a": ["loss of appetite", "vomiting", "dark urine", "jaundice"],
    "leptospirosis": ["fever", "headache", "calf pain", "red eyes"]
}

def classify_urgency(text: str) -> dict:
    """
    Checks for emergency and PHC keywords in text and returns classification dict.
    Three levels: EMERGENCY (red), VISIT_PHC (yellow), SELF_CARE (green)
    """
    text_lower = text.lower()
    
    # Check for EMERGENCY keywords first
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return {
                "level": "EMERGENCY",
                "action": "Seek immediate medical attention. Go to the nearest emergency department or call emergency services.",
                "color": "red"
            }

    # Check for high-risk conditions that warrant a PHC visit even when mentioned alone
    for keyword in HIGH_RISK_PHC_KEYWORDS:
        if keyword in text_lower:
            return {
                "level": "VISIT_PHC",
                "action": "This may need medical attention. Please visit your nearest Primary Health Centre (PHC) for evaluation and care.",
                "color": "yellow"
            }

    # Check for disease-specific symptom combinations where ALL symptoms must appear together
    for disease, symptoms in SYMPTOM_COMBINATIONS.items():
        if all(sym in text_lower for sym in symptoms):
            return {
                "level": "VISIT_PHC",
                "action": f"Your symptoms match a pattern associated with {disease.title()}. Please visit your nearest Primary Health Centre (PHC) for a medical evaluation.",
                "color": "yellow"
            }
            
    # Check for PHC keywords next (require 2 or more together)
    matched_phc = [keyword for keyword in PHC_KEYWORDS if keyword in text_lower]
    if len(matched_phc) >= 2:
        return {
            "level": "VISIT_PHC",
            "action": "Please visit your nearest Primary Health Centre (PHC) for a medical evaluation.",
            "color": "yellow"
        }
            
    # Default to SELF_CARE
    return {
        "level": "SELF_CARE",
        "action": "Monitor your symptoms, rest, keep hydrated, and practice self-care. If symptoms persist or worsen, consult a doctor.",
        "color": "green"
    }

def triage_symptoms(text: str) -> Dict[str, Any]:
    """
    Analyzes symptoms and returns severity and recommended actions.
    """
    urgency = classify_urgency(text)
    
    # Map the level to severity
    severity_map = {
        "EMERGENCY": "emergency",
        "VISIT_PHC": "medium",
        "SELF_CARE": "low"
    }
    
    # Extract symptoms that matched
    matched_symptoms = []
    text_lower = text.lower()
    for kw in EMERGENCY_KEYWORDS + HIGH_RISK_PHC_KEYWORDS + PHC_KEYWORDS:
        if kw in text_lower:
            matched_symptoms.append(kw.title())
            
    return {
        "symptoms": matched_symptoms,
        "severity": severity_map.get(urgency["level"], "low"),
        "recommended_action": urgency["action"],
        "suggested_specialist": "Emergency Medicine" if urgency["level"] == "EMERGENCY" else "General Physician"
    }

