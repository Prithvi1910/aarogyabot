import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA

# Relative import of get_retriever
from .retriever import get_retriever

# Load environment variables
load_dotenv()

def get_llm():
    """
    Loads GROQ_API_KEY from environment
    Returns a ChatGroq instance using model "llama-3.1-8b-instant" with temperature 0.2
    If GROQ_API_KEY is not set, falls back to Ollama with model "llama3.2"
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key.strip():
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            groq_api_key=groq_api_key.strip()
        )
    else:
        return Ollama(
            model="llama3.2",
            temperature=0.2
        )

HEALTH_PROMPT = PromptTemplate.from_template(
    "You are AarogyaBot, a top-level expert doctor and highly experienced medical professional.\n"
    "Answer using ONLY the provided context, but be highly descriptive, precise, and authoritative in your medical assessment.\n"
    "Act with deep clinical empathy while providing professional, comprehensive advice.\n"
    "Do not mention that you are an AI.\n\n"
    "STRICT RULES:\n"
    "1. You MUST provide descriptive medical assessments based on the user's symptoms.\n"
    "2. Explicitly recommend the appropriate medicines and treatments for the conditions or symptoms described, based on the provided context.\n"
    "3. Explain the reasoning behind your medical advice like a top-level physician would to a patient.\n"
    "4. Clearly advise on when the patient should immediately visit an emergency room or a Primary Health Centre (PHC) for physical evaluation.\n"
    "5. Answer using ONLY the provided context. Do not invent medical information.\n"
    "6. AVOID REPETITIVE ANSWERS: Do not repeat the exact same phrasing. Vary your language and provide tailored, dynamic responses.\n\n"
    "Context: {context}\n"
    "Question: {question}\n\n"
    "Answer as an expert doctor in a highly descriptive, professional, and empathetic manner:"
)

def get_answer(query: str) -> str:
    """
    Builds a RetrievalQA chain using get_llm() and get_retriever()
    Uses the HEALTH_PROMPT
    Returns the answer string
    Wraps everything in try/except and returns a safe fallback message on error
    """
    try:
        llm = get_llm()
        retriever = get_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": HEALTH_PROMPT}
        )
        response = qa_chain.invoke({"query": query})
        if isinstance(response, dict):
            return response.get("result", "").strip()
        return str(response).strip()
    except Exception as e:
        print(f"Error in get_answer: {e}")
        return "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."

def generate_response(query: str, context: List[Dict[str, Any]] = None) -> str:
    """
    Generates a response from the LLM based on user query and retrieved health contexts.
    """
    return get_answer(query)
