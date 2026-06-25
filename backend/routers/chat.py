from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
import json

# Import schemas and DB helper from models
from models import get_db, ChatRequest, ChatResponse, FacilityResult

# Import pipeline functions
from pipeline import (
    detect_language,
    to_english,
    from_english,
    classify_urgency,
    get_answer,
    get_answer_with_history,
)
from pipeline.generator import stream_answer

from routers.facilities import get_facilities_by_pincode

SESSION_STORE = {}

router = APIRouter(prefix="/chat", tags=["Chat & Triage"])

@router.post("/", response_model=ChatResponse)
def post_chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Receive user chat message, detect language, retrieve health documentation,
    generate AI response in detected language, and save session log to DB.
    """
    detected_lang = "en"
    session_id = payload.session_id if payload.session_id else str(uuid4())
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
                facilities=facility_results,
                session_id=session_id
            )
        
        # Non-PIN code flow
        english_msg = to_english(message, detected_lang)
        triage = classify_urgency(english_msg)
        
        # Look up SESSION_STORE[session_id] for history (default [])
        history = SESSION_STORE.get(session_id, [])
        
        # Pass history to get_answer_with_history() instead of get_answer()
        answer = get_answer_with_history(english_msg, history)
        translated_reply = from_english(answer, detected_lang)
        
        # After reply, append user message and bot reply to history
        history.append(english_msg)
        history.append(answer)
        
        # Trim history to last 6 messages
        history = history[-6:]
        
        # Save back to SESSION_STORE[session_id]
        SESSION_STORE[session_id] = history
        
        return ChatResponse(
            reply=translated_reply,
            triage=triage,
            facilities=[],
            session_id=session_id
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
            facilities=[],
            session_id=session_id
        )

@router.post("/stream")
async def post_chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Receive user chat message, detect language, retrieve health documentation,
    stream AI response, and return StreamingResponse.
    """
    detected_lang = "en"
    session_id = payload.session_id if payload.session_id else str(uuid4())
    try:
        message = payload.message.strip()
        detected_lang = detect_language(message)
        
        # Check if message is a PIN code
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
                {
                    "name": f["name"],
                    "type": f["type"],
                    "district": f["district"],
                    "phone": f.get("phone") or None,
                    "distance_km": 0.0
                }
                for f in facilities
            ]
            
            async def pin_generator():
                yield f"data: {reply}\n\n"
                done_data = {
                    "triage": {},
                    "facilities": facility_results,
                    "session_id": session_id
                }
                yield f"data: [DONE]{json.dumps(done_data)}\n\n"
                
            return StreamingResponse(pin_generator(), media_type="text/event-stream")

        # Non-PIN code flow
        english_msg = to_english(message, detected_lang)
        triage = classify_urgency(english_msg)
        
        history = SESSION_STORE.get(session_id, [])
        
        async def response_generator():
            full_reply_en = ""
            try:
                async for chunk in stream_answer(english_msg, history):
                    full_reply_en += chunk
                    yield f"data: {chunk}\n\n"
            except Exception as stream_err:
                print(f"Error in response generator: {stream_err}")
                yield f"data: I am sorry, I am having trouble answering right now.\n\n"
                
            history.append(english_msg)
            history.append(full_reply_en)
            SESSION_STORE[session_id] = history[-6:]
            
            done_data = {
                "triage": triage,
                "facilities": [],
                "session_id": session_id
            }
            yield f"data: [DONE]{json.dumps(done_data)}\n\n"
            
        return StreamingResponse(response_generator(), media_type="text/event-stream")
        
    except Exception as e:
        async def fallback_generator():
            fallback_en = "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."
            try:
                fallback_reply = from_english(fallback_en, detected_lang)
            except Exception:
                fallback_reply = fallback_en
            yield f"data: {fallback_reply}\n\n"
            done_data = {
                "triage": {},
                "facilities": [],
                "session_id": session_id
            }
            yield f"data: [DONE]{json.dumps(done_data)}\n\n"
        return StreamingResponse(fallback_generator(), media_type="text/event-stream")

@router.post("/triage")
def post_triage_symptoms(payload: ChatRequest):
    """
    Analyze chat session symptoms and return severity status and recommended actions.
    """
    # - Implement triage logic using triage pipeline component
    raise HTTPException(status_code=501, detail="Endpoint not implemented yet.")

