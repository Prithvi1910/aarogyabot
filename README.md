# Aarogyabot (आरोग्यबॉट)

Aarogyabot is a full-stack multilingual healthcare assistance chatbot designed to support medical triage, facility locating, and patient-doctor queries. The name **Aarogya** (आरोग्य) comes from Sanskrit, meaning "health" or "freedom from disease."

## Project Overview

Aarogyabot acts as a medical assistant that can:
1. **Understand Multilingual Queries**: Auto-detect user's native language (e.g. Hindi, Tamil, Telugu, etc.) and translate/respond appropriately.
2. **Retrieve Health Information**: Use a retrieve-and-generate (RAG) pipeline to fetch verified health documentation.
3. **Perform Intelligent Triage**: Classify symptoms and direct users to appropriate levels of care (self-care, primary care clinic, or emergency).
4. **Locate Healthcare Facilities**: Search and guide users to nearest Primary Health Centers (PHCs) and government hospitals.

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
