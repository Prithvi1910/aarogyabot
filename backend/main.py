import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables on startup
load_dotenv()

# Import routers
from routers.chat import router as chat_router
from routers.webhook import router as webhook_router
from routers.facilities import router as facilities_router

app = FastAPI(
    title="Aarogyabot API",
    description="Multilingual medical triage and healthcare facilities assistant",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(webhook_router)
app.include_router(facilities_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Build PHC database if it doesn't exist
    if not os.path.exists("data/phc_database.sqlite"):
        print("Building PHC database...")
        import subprocess
        subprocess.run(["python", "data/build_phc_db.py"])
        print("PHC database built")

    # Build FAISS index if it doesn't exist
    if not os.path.exists("data/faiss_index"):
        print("Building FAISS index...")
        from pipeline.retriever import build_index
        build_index()
        print("FAISS index built")
