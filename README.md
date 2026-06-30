# Aarogyabot (आरोग्यबॉट)

Aarogyabot is a full-stack multilingual healthcare assistance chatbot designed to support medical triage, facility locating, and patient-doctor queries. The name **Aarogya** (आरोग्य) comes from Sanskrit, meaning "health" or "freedom from disease."

## Project Overview

Aarogyabot acts as a medical assistant that can:
1. **Understand Multilingual Queries**: Auto-detect user's native language (e.g. Hindi, Tamil, Telugu, etc.) and translate/respond appropriately.
2. **Retrieve Health Information**: Use a retrieve-and-generate (RAG) pipeline to fetch verified health documentation.
3. **Perform Intelligent Triage**: Classify symptoms and direct users to appropriate levels of care (self-care, primary care clinic, or emergency).
4. **Locate Healthcare Facilities**: Search and guide users to nearest Primary Health Centers (PHCs) and government hospitals.
5. **Visual Symptom Checker**: Accept a photo of a visible concern (rash, wound, eye, snake-bite) and use a Groq vision model to describe it, run triage, and reply in the user's language — removing the literacy and vocabulary barrier for rural users.
6. **Voice Output (Read Aloud)**: Every bot reply can be spoken aloud in the user's language via on-device Speech Synthesis, with a per-message "Listen" button and a header toggle to auto-read replies — pairing with the existing voice input for a full see–speak–listen experience for low-literacy users.
7. **Community Outbreak Surveillance**: Anonymized symptom signals from ordinary chats are aggregated into regional clusters and surfaced on a live alerts dashboard (likely disease, PIN area, severity) — an early-warning epidemiology layer. Endpoint `GET /surveillance/alerts`.
8. **GPS Facility Finder + SOS-108**: One tap uses device GPS to find the nearest PHCs (via `/facilities/nearby`), and emergency triage cards show a one-tap "Call 108 Ambulance" button.
9. **Source Citations**: Text answers cite the health docs they were grounded in, for transparency and anti-hallucination.
10. **Installable Offline PWA**: Installs to the home screen and works without a network — a bundled first-aid pack answers safely offline (critical for 2G / no-signal rural areas).

## Answer Quality & Knowledge Base

- **Stronger model**: answers use `llama-3.3-70b-versatile` by default (configurable via `GROQ_MODEL`) for better medical accuracy.
- **Grounded prompt**: the assistant answers only from retrieved health docs, refuses to invent facts, and follows strict OTC-only medicine-safety rules (no prescription drugs/dosages; Paracetamol-only guidance for dengue).
- **Better retrieval**: larger chunks (900/150) keep each condition's full entry together; top-k raised to 6.
- **Expanded corpus** (19 documents): added nutrition & anaemia, animal bites & rabies, first-aid emergencies, extended skin infections, digestive & urinary conditions, a safe-medications guide, and immunization & prevention.
- **Sharper triage**: expanded emergency keywords (snake bite, drowning, choking, severe bleeding, etc.) and high-risk single-keyword PHC flags (animal bites/rabies, jaundice, fractures).

## Visual Symptom Checker

Users can tap the camera button in the chat to send a photo of a visible health concern. The backend:

1. Sends the image to a **Groq vision model** (`GROQ_VISION_MODEL`, default `meta-llama/llama-4-scout-17b-16e-instruct`) with a cautious public-health prompt that describes only what is visible and never gives a definite diagnosis.
2. Runs the existing rule-based **triage** on the observation (Emergency / Visit-PHC / Self-care).
3. Grounds follow-up advice in the **RAG** health docs and re-uses the chat session history.
4. Translates the reply into the user's language.

**Endpoint:** `POST /chat/image` (multipart form: `file`, optional `note`, `session_id`, `lang`). Requires `GROQ_API_KEY`.

## Directory Structure

```
aarogyabot/
├── backend/                  # FastAPI Application (Python 3.11)
│   ├── main.py              # Application entrypoint
│   ├── requirements.txt      # Dependency list
│   ├── .env.example          # Environment configuration template
│   ├── routers/             # API Router endpoints
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat & interaction endpoints
│   │   ├── webhook.py       # WhatsApp / Messaging integrations
│   │   └── facilities.py    # Health facility lookup endpoints
│   ├── pipeline/            # RAG and LLM logic
│   │   ├── __init__.py
│   │   ├── detect_lang.py   # Language detection
│   │   ├── translate.py     # Translation service
│   │   ├── retriever.py     # Vector DB search / document search
│   │   ├── generator.py     # LLM answer generation
│   │   └── triage.py        # Rule & LLM based medical triage
│   ├── models/              # DB Models & schemas
│   │   ├── __init__.py
│   │   ├── db.py            # Database configuration
│   │   └── schemas.py       # Pydantic validation schemas
│   └── data/                # Data storage and build scripts
│       ├── health_docs/     # Reference medical guides (PDFs/Txt)
│       └── build_phc_db.py  # Seeding script for PHC database
└── frontend/                 # React Application (React + Vite + Tailwind CSS)
    ├── package.json          # Node dependencies and scripts
    ├── tailwind.config.js    # Tailwind layout customizations
    ├── postcss.config.js     # PostCSS loader config
    ├── vite.config.js        # Vite build tool config
    ├── index.html            # Main SPA index file
    ├── .env.example          # Frontend API configurations
    └── src/
        ├── App.jsx           # Root layout component
        ├── main.jsx          # React renderer mount point
        ├── index.css         # Tailwind global styles
        └── components/       # Interface component library
            ├── ChatInterface.jsx # Chat panel and inputs
            ├── MessageBubble.jsx # Render chat dialogs
            ├── TriageCard.jsx    # Display triage instructions
            └── FacilityCard.jsx  # Show nearby medical facility details
```

## Getting Started

### Backend Setup
1. Navigate to `/backend`:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in API keys:
   ```bash
   copy .env.example .env
   ```
5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to `/frontend`:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
4. Run the Vite dev server:
   ```bash
   npm run dev
   ```
