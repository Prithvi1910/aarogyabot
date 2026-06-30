from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

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
    get_answer_with_sources,
    analyze_medical_image,
)
from pipeline.generator import generate_health_report
from pipeline.triage import triage_symptoms

from routers.facilities import get_facilities_by_pincode
from routers.surveillance import log_report

SESSION_STORE = {}
# Last known PIN code per session, used to geo-tag anonymized surveillance reports
SESSION_PINCODE = {}

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
            # Remember the area for anonymized surveillance geo-tagging
            SESSION_PINCODE[session_id] = message
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
                session_id=session_id,
                lang=detected_lang
            )
        
        # Non-PIN code flow
        english_msg = to_english(message, detected_lang)
        triage = classify_urgency(english_msg)

        # Look up SESSION_STORE[session_id] for history (default [])
        history = SESSION_STORE.get(session_id, [])

        # Generate a grounded answer along with its health-doc sources
        result = get_answer_with_sources(english_msg, history)
        answer = result["answer"]
        sources = result.get("sources", [])
        translated_reply = from_english(answer, detected_lang)

        # Feed anonymized symptom signal into community surveillance
        try:
            detected_symptoms = triage_symptoms(english_msg).get("symptoms", [])
            if detected_symptoms:
                log_report(SESSION_PINCODE.get(session_id), detected_symptoms, triage.get("level"))
        except Exception as se:
            print(f"Surveillance logging failed: {se}")

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
            session_id=session_id,
            lang=detected_lang,
            sources=sources
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
            session_id=session_id,
            lang=detected_lang
        )


@router.post("/image", response_model=ChatResponse)
async def post_chat_image(
    file: UploadFile = File(...),
    note: str = Form(""),
    session_id: Optional[str] = Form(None),
    lang: str = Form("en"),
):
    """
    Visual symptom checker: accept a photo of a health concern (rash, wound, eye,
    snake-bite, etc.), analyse it with the Groq vision model, run rule-based triage
    on the observation, ground follow-up advice in the RAG health docs, and reply
    in the user's language.
    """
    session_id = session_id if session_id else str(uuid4())

    # Resolve the target language. "auto" + a typed note => detect from the note.
    target_lang = (lang or "en").strip() or "en"
    if target_lang == "auto":
        target_lang = detect_language(note) if note and note.strip() else "en"

    # Validate the upload is an image.
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")

        # The user's note may be in their own language; translate it to English for the model.
        note_en = note
        if note and note.strip() and target_lang != "en":
            note_en = to_english(note, target_lang)

        # 1) Vision analysis -> concise English observation.
        observation_en = analyze_medical_image(image_bytes, content_type, note_en)

        # 2) Rule-based triage on the observation.
        triage = classify_urgency(observation_en)

        # 3) Ground next-step advice in the health docs (RAG), reusing session history.
        history = SESSION_STORE.get(session_id, [])
        reply_en = observation_en
        try:
            guidance_en = get_answer_with_history(observation_en, history)
            fallback = "I am sorry, I am having trouble answering right now."
            if guidance_en and fallback not in guidance_en and guidance_en.strip() != observation_en.strip():
                reply_en = f"{observation_en}\n\n{guidance_en}"
        except Exception as ge:
            print(f"Image RAG guidance failed: {ge}")

        # 4) Translate the final reply into the user's language.
        translated_reply = from_english(reply_en, target_lang)

        # 5) Persist to session history so the health report includes the image visit.
        history.append(f"[Sent a photo] {note_en}".strip())
        history.append(reply_en)
        SESSION_STORE[session_id] = history[-6:]

        return ChatResponse(
            reply=translated_reply,
            triage=triage,
            facilities=[],
            session_id=session_id,
            lang=target_lang,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in post_chat_image: {e}")
        fallback_en = (
            "I could not analyse this photo right now. If you have a visible health "
            "concern, please show it to a health worker at your nearest PHC."
        )
        try:
            fallback_reply = from_english(fallback_en, target_lang)
        except Exception:
            fallback_reply = fallback_en
        return ChatResponse(
            reply=fallback_reply,
            triage={},
            facilities=[],
            session_id=session_id,
            lang=target_lang,
        )


@router.post("/triage")
def post_triage_symptoms(payload: ChatRequest):
    """
    Analyze chat session symptoms and return severity status and recommended actions.
    """
    # - Implement triage logic using triage pipeline component
    raise HTTPException(status_code=501, detail="Endpoint not implemented yet.")


class ReportRequest(BaseModel):
    session_id: str


@router.post("/report")
def post_generate_report(payload: ReportRequest):
    """
    Generate a structured health summary report from a session's conversation history.
    """
    history = SESSION_STORE.get(payload.session_id)
    if not history:
        raise HTTPException(status_code=404, detail="No conversation found for this session.")

    report = generate_health_report(history)
    return {
        "report": report,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
