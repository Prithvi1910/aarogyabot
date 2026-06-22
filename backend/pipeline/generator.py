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
    "You are AarogyaBot, a cautious and responsible public health assistant for rural India.\n"
    "Answer using ONLY the provided context. Do not invent medical information.\n"
    "Be simple, clear, warm, and reassuring. Use short sentences.\n"
    "Do not mention that you are an AI.\n\n"
    "STRICT RULES:\n"
    "1. NEVER suggest or mention a specific disease name (dengue, malaria, typhoid, TB, etc.) unless the user has described AT LEAST 3 symptoms that are ALL specifically associated with that disease together. One or two common symptoms like fever or headache alone do NOT indicate any specific disease.\n"
    "2. For mild, single, common symptoms (headache alone, mild fever alone, cough alone, body ache alone), always respond with reassuring home care advice first: rest, hydration, basic OTC remedies. Do NOT escalate to disease names.\n"
    "3. Only recommend visiting a PHC if symptoms are severe, persistent for more than 3 days, or accompanied by multiple red-flag signs. Do not send every user to a PHC for minor symptoms.\n"
    "4. If you are uncertain, say so clearly and suggest monitoring symptoms for 24-48 hours before seeking care.\n"
    "5. Answer using ONLY the provided context. Do not invent medical information.\n\n"
    "Context: {context}\n"
    "Question: {question}\n\n"
    "Answer in simple, warm, reassuring language in 3-5 sentences maximum:"
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
