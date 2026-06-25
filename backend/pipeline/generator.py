import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
import uuid

SESSION_MEMORIES = {}

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
    "Be simple, clear, and very concise. Keep your answers short and crisp.\n"
    "Provide the most useful information and explicitly state any recommended medicines or cures based on the context.\n"
    "If the symptom is severe, briefly advise visiting the nearest Primary Health Centre (PHC).\n\n"
    "STRICT RULES:\n"
    "1. Keep answers short and crisp (maximum 2-3 short sentences if possible).\n"
    "2. AVOID REPETITIVE ANSWERS: Do not repeat the exact same phrasing. Vary your language.\n"
    "STRICT RULE 6: For medicine/medication questions:\n"
    "- You CAN mention safe, common over-the-counter remedies for mild symptoms (paracetamol for fever, ORS for diarrhea, clean water and rest for dehydration)\n"
    "- Always add: 'For prescription medicines, please consult a doctor at your nearest PHC'\n"
    "- NEVER recommend prescription drugs, antibiotics, or specific dosages\n"
    "- NEVER say you cannot help — always give the safe OTC option first, then refer to PHC for anything stronger\n\n"
    "Context: {context}\n"
    "Question: {question}\n\n"
    "Answer concisely and clearly:"
)

def get_answer(query: str, session_id: str = None) -> str:
    """
    Builds a ConversationalRetrievalChain using get_llm() and get_retriever()
    Uses the HEALTH_PROMPT
    Returns the answer string
    Wraps everything in try/except and returns a safe fallback message on error
    """
    try:
        llm = get_llm()
        retriever = get_retriever()
        
        if not session_id:
            session_id = str(uuid.uuid4())
            
        if session_id not in SESSION_MEMORIES:
            SESSION_MEMORIES[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
        memory = SESSION_MEMORIES[session_id]
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": HEALTH_PROMPT}
        )
        
        response = qa_chain.invoke({"question": query})
        if isinstance(response, dict):
            return response.get("answer", "").strip()
        return str(response).strip()
    except Exception as e:
        print(f"Error in get_answer: {e}")
        return "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."

def generate_response(query: str, context: List[Dict[str, Any]] = None, session_id: str = None) -> str:
    """
    Generates a response from the LLM based on user query and retrieved health contexts.
    """
    return get_answer(query, session_id)

def get_answer_with_history(query: str, history: list = []) -> str:
    """
    Generate an answer using RAG and prepend conversation history to the prompt.
    """
    try:
        if not history:
            return get_answer(query)
        
        # Keep last 6 messages only
        trimmed_history = history[-6:]
        
        # Format history
        formatted_history = "Previous conversation:\n"
        for i in range(0, len(trimmed_history), 2):
            if i + 1 < len(trimmed_history):
                formatted_history += f"User: {trimmed_history[i]}\nAssistant: {trimmed_history[i+1]}\n"
                
        # Prepend formatted history to the question in the prompt
        prepended_query = formatted_history + query
        
        llm = get_llm()
        retriever = get_retriever()
        
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": HEALTH_PROMPT}
        )
        
        response = qa_chain.invoke({"question": prepended_query})
        if isinstance(response, dict):
            return response.get("answer", "").strip()
        return str(response).strip()
    except Exception as e:
        print(f"Error in get_answer_with_history: {e}")
        return "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."

