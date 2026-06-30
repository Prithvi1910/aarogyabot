import os
import base64
from dotenv import load_dotenv

load_dotenv()

# Groq hosts multimodal (vision) models. Default to Llama 4 Scout, overridable via env.
VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

# Cautious system instruction tuned for rural public-health triage.
VISION_SYSTEM_PROMPT = (
    "You are AarogyaBot, a cautious public-health visual assistant for rural India. "
    "You are shown a photo of a possible health concern (e.g. a skin rash, wound, "
    "burn, swelling, eye, snake-bite, or insect bite). "
    "Describe ONLY what is clearly visible in plain, simple English. "
    "Then name the 1-2 most likely COMMON conditions it could be, always saying 'possibly' "
    "or 'may be' — never give a definite diagnosis. "
    "If the image shows signs that could be serious (heavy bleeding, deep wound, snake-bite, "
    "spreading infection, severe burn, blue/grey skin, eye injury), clearly say it needs "
    "urgent care. "
    "Keep the whole reply to 2-4 short sentences. "
    "If the photo is not a clear medical image (no visible body part or condition), say so "
    "and ask the user to retake a clear, well-lit photo."
)


def _to_data_url(image_bytes: bytes, mime_type: str) -> str:
    """Encode raw image bytes into a base64 data URL for the Groq vision API."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"
    return f"data:{mime_type};base64,{b64}"


def analyze_medical_image(image_bytes: bytes, mime_type: str = "image/jpeg", note: str = "") -> str:
    """
    Send an image to the Groq vision model and return a concise English observation
    of the visible health concern. Raises on misconfiguration; returns a safe fallback
    string on model/runtime errors so the caller can still respond gracefully.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or not groq_api_key.strip():
        raise ValueError("GROQ_API_KEY not set; vision analysis requires a Groq API key.")

    # Imported lazily so the rest of the app loads even if the SDK is missing.
    from groq import Groq

    client = Groq(api_key=groq_api_key.strip())
    data_url = _to_data_url(image_bytes, mime_type)

    user_text = "Please look at this photo and describe the visible health concern."
    if note and note.strip():
        user_text += f" The person also said: \"{note.strip()}\""

    try:
        completion = client.chat.completions.create(
            model=VISION_MODEL,
            temperature=0.2,
            max_tokens=300,
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in analyze_medical_image: {e}")
        return (
            "I could not clearly analyse this photo. If you have a visible health concern, "
            "please show it to a health worker at your nearest PHC."
        )
