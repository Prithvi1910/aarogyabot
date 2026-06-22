from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Import schemas and DB helper from models
from models import get_db, ChatRequest, ChatResponse, FacilityResult

# Import pipeline functions
from pipeline import (
    detect_language,
    to_english,
    from_english,
    classify_urgency,
    get_answer,
)

from routers.facilities import get_facilities_by_pincode

router = APIRouter(prefix="/chat", tags=["Chat & Triage"])

@router.post("/", response_model=ChatResponse)
def post_chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Receive user chat message, detect language, retrieve health documentation,
    generate AI response in detected language, and save session log to DB.
    """
    detected_lang = "en"
    try:
        message = payload.message.strip()
        detected_lang = detect_language(message)
        
        # Check if message is a PIN code (all digits, 6 characters)
        if len(message) == 6 and message.isdigit():
            facilities = get_facilities_by_pincode(message)
            if not facilities:
                reply = f"No facilities found for PIN code {message}."
            else:
                reply = f"Found the following facilities for PIN code {message}:\n"
                for idx, f in enumerate(facilities, 1):
                    phone_str = f" (Phone: {f['phone']})" if f.get("phone") else ""
                    reply += f"{idx}. {f['name']} ({f['type']}) - {f['district']}{phone_str}\n"
            
            facility_results = [
                FacilityResult(
                    name=f["name"],
                    type=f["type"],
                    district=f["district"],
                    phone=f.get("phone") or None,
                    distance_km=0.0
                )
                for f in facilities
            ]
            return ChatResponse(
                reply=reply.strip(),
                triage={},
                facilities=facility_results
            )
        
        # Non-PIN code flow
        english_msg = to_english(message, detected_lang)
        triage = classify_urgency(english_msg)
        answer = get_answer(english_msg, payload.session_id)
        translated_reply = from_english(answer, detected_lang)
        
        return ChatResponse(
            reply=translated_reply,
            triage=triage,
            facilities=[]
        )
        
    except Exception as e:
        fallback_en = "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."
        try:
            fallback_reply = from_english(fallback_en, detected_lang)
        except Exception:
            fallback_reply = fallback_en
        
        return ChatResponse(
            reply=fallback_reply,
            triage={},
            facilities=[]
        )

@router.post("/triage")
def post_triage_symptoms(payload: ChatRequest):
    """
    Analyze chat session symptoms and return severity status and recommended actions.
    """
    # - Implement triage logic using triage pipeline component
    raise HTTPException(status_code=501, detail="Endpoint not implemented yet.")

