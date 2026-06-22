import re
from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse

# Import pipeline functions
from pipeline import (
    detect_language,
    to_english,
    from_english,
    classify_urgency,
    get_answer,
)

from routers.facilities import get_facilities_by_pincode

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

def format_for_sms(reply: str, triage: dict, facilities: list) -> str:
    """
    Format response for SMS:
    - Strips all markdown formatting (no asterisks, no bullet points, no newlines replaced with spaces)
    - Truncates the reply to maximum 140 characters
    - Appends triage action and first facility name + phone if present
    - Total message fit within 320 characters
    """
    text = reply.replace("*", "").replace("_", "").replace("#", "")
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r'^\s*-\s+', '', text)
    text = re.sub(r'\s+-\s+', ' ', text)
    text = " ".join(text.split())
    
    if len(text) > 140:
        text = text[:140]
        
    parts = [text]
    
    level = triage.get("level")
    if level == "EMERGENCY":
        parts.append("EMERGENCY: Call 108")
    elif level == "VISIT_PHC":
        parts.append("Visit PHC soon.")
        
    if facilities:
        f = facilities[0]
        name = f.get("name", "")
        phone = f.get("phone", "")
        phone_str = f" {phone}" if phone else ""
        parts.append(f"Nearest: {name}{phone_str}")
        
    final_sms = " ".join([p for p in parts if p])
    if len(final_sms) > 320:
        final_sms = final_sms[:320]
    return final_sms

def format_for_whatsapp(reply: str, triage: dict, facilities: list) -> str:
    """
    Format response for WhatsApp:
    - Keeps full response with proper line breaks
    - Adds triage action on a new line with an appropriate emoji prefix
    - Lists up to 3 facilities with name, type and phone
    - No character limit
    """
    lines = [reply]
    level = triage.get("level")
    action = triage.get("action")
    
    if level == "EMERGENCY":
        prefix = "⚠️"
        if action:
            lines.append(f"{prefix} {action}")
    elif level == "VISIT_PHC":
        prefix = "🏥"
        if action:
            lines.append(f"{prefix} {action}")
            
    if facilities:
        lines.append("Nearest Facilities:")
        for idx, f in enumerate(facilities[:3], 1):
            phone_str = f" (Phone: {f['phone']})" if f.get("phone") else ""
            lines.append(f"{idx}. {f['name']} ({f['type']}) - {f['district']}{phone_str}")
            
    return "\n".join(lines)

def process_webhook_message(body: str, from_number: str, force_sms: bool = False) -> str:
    detected_lang = "en"
    try:
        message = body.strip()
        detected_lang = detect_language(message)
        
        is_sms = force_sms or (not from_number.startswith("whatsapp:"))
        
        triage = {}
        facilities = []
        reply = ""
        
        # Check if message is a PIN code (all digits, 6 characters)
        if len(message) == 6 and message.isdigit():
            facilities = get_facilities_by_pincode(message)
            if not facilities:
                reply = f"No facilities found for PIN code {message}."
            else:
                reply = f"Found facilities for PIN {message}:"
        else:
            # Non-PIN code flow
            english_msg = to_english(message, detected_lang)
            triage = classify_urgency(english_msg)
            answer = get_answer(english_msg)
            reply = from_english(answer, detected_lang)
            if triage.get("action"):
                triage["action"] = from_english(triage["action"], detected_lang)
                
        if is_sms:
            return format_for_sms(reply, triage, facilities)
        else:
            return format_for_whatsapp(reply, triage, facilities)
            
    except Exception as e:
        print(f"Error in process_webhook_message: {e}")
        fallback_en = "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."
        try:
            fallback_reply = from_english(fallback_en, detected_lang)
        except Exception:
            fallback_reply = fallback_en
        return fallback_reply

@router.get("/whatsapp")
def verify_whatsapp_webhook():
    """
    Handle WhatsApp Webhook verification challenge (GET request) by returning 200 OK.
    """
    return Response(content="OK", status_code=200)

@router.post("/whatsapp")
async def post_whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Receive incoming messages from WhatsApp webhook (POST request), process,
    and reply with formatted XML message (SMS-optimized or WhatsApp-optimized).
    """
    reply_content = process_webhook_message(Body, From, force_sms=False)
    twiml_resp = MessagingResponse()
    twiml_resp.message(reply_content)
    return Response(content=str(twiml_resp), media_type="application/xml")

@router.get("/sms")
def verify_sms_webhook():
    """
    Handle SMS Webhook verification challenge (GET request) by returning 200 OK.
    """
    return Response(content="OK", status_code=200)

@router.post("/sms")
async def post_sms_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Receive incoming messages from SMS webhook (POST request), force SMS formatting,
    and reply with formatted XML message.
    """
    reply_content = process_webhook_message(Body, From, force_sms=True)
    twiml_resp = MessagingResponse()
    twiml_resp.message(reply_content)
    return Response(content=str(twiml_resp), media_type="application/xml")
