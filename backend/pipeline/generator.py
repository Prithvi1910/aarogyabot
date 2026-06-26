import os
from typing import List, Dict, Any, AsyncGenerator
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
    Builds the prompt manually by fetching context and querying the LLM directly.
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        context_str = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = HEALTH_PROMPT.format(context=context_str, question=query)
        llm = get_llm()
        
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            return response.content.strip()
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
        retriever = get_retriever()
        docs = retriever.invoke(query)
        context_str = "\n\n".join([doc.page_content for doc in docs])
        
        prepended_query = query
        if history:
            trimmed_history = history[-6:]
            formatted_history = "Previous conversation:\n"
            for i in range(0, len(trimmed_history), 2):
                if i + 1 < len(trimmed_history):
                    formatted_history += f"User: {trimmed_history[i]}\nAssistant: {trimmed_history[i+1]}\n"
            prepended_query = formatted_history + "\nCurrent Query:\n" + query
            
        prompt = HEALTH_PROMPT.format(context=context_str, question=prepended_query)
        
        llm = get_llm()
        response = llm.invoke(prompt)
        
        if hasattr(response, "content"):
            return response.content.strip()
        return str(response).strip()
    except Exception as e:
        print(f"Error in get_answer_with_history: {e}")
        return "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."

async def stream_answer(query: str, history: list = []) -> AsyncGenerator[str, None]:
    """
    Async generator that yields response chunks from ChatGroq with streaming.
    """
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key or not groq_api_key.strip():
            raise ValueError("GROQ_API_KEY not set")
            
        retriever = get_retriever()
        docs = retriever.invoke(query)
        context_str = "\n\n".join([doc.page_content for doc in docs])
        
        prepended_query = query
        if history:
            trimmed_history = history[-6:]
            formatted_history = "Previous conversation:\n"
            for i in range(0, len(trimmed_history), 2):
                if i + 1 < len(trimmed_history):
                    formatted_history += f"User: {trimmed_history[i]}\nAssistant: {trimmed_history[i+1]}\n"
            prepended_query = formatted_history + query
            
        prompt = HEALTH_PROMPT.format(context=context_str, question=prepended_query)
        
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            groq_api_key=groq_api_key.strip(),
            streaming=True
        )
        
        async for chunk in llm.astream(prompt):
            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            if content:
                yield content
                
    except Exception as e:
        print(f"Streaming failed, falling back to non-streaming: {e}")
        try:
            if history:
                ans = get_answer_with_history(query, history)
            else:
                ans = get_answer(query)
            yield ans
        except Exception:
            yield "I am sorry, I am having trouble answering right now. Please visit your nearest PHC."


def generate_health_report(conversation: list) -> str:
    """
    Takes conversation history as a flat list of alternating user/assistant strings.
    Builds a structured health summary prompt and calls the Groq LLM directly (no RAG).
    Returns a formatted report string.
    """
    try:
        if not conversation:
            return "No conversation history available to generate a report."

        # Format the conversation into a readable transcript
        transcript_lines = []
        for i in range(0, len(conversation), 2):
            user_msg = conversation[i] if i < len(conversation) else ""
            bot_msg = conversation[i + 1] if i + 1 < len(conversation) else ""
            if user_msg:
                transcript_lines.append(f"Patient: {user_msg}")
            if bot_msg:
                transcript_lines.append(f"Health Assistant: {bot_msg}")

        transcript = "\n".join(transcript_lines)

        report_prompt = (
            "Based on this conversation between a patient and a health assistant, "
            "generate a concise health summary report with these sections:\n\n"
            "PATIENT SYMPTOMS: (list all symptoms mentioned)\n"
            "DURATION & SEVERITY: (extract any time/severity info)\n"
            "TRIAGE LEVEL: (Self-care / Visit PHC / Emergency)\n"
            "HOME CARE ADVISED: (list home care steps given)\n"
            "WHEN TO SEEK CARE: (specific warning signs to watch for)\n"
            "NEAREST FACILITY: (placeholder: Visit your nearest PHC)\n\n"
            "Keep it simple, in plain English, suitable for showing to a doctor. "
            "Maximum 200 words.\n\n"
            f"Conversation:\n{transcript}\n\n"
            "Health Summary Report:"
        )

        llm = get_llm()
        response = llm.invoke(report_prompt)
        if hasattr(response, "content"):
            return response.content.strip()
        return str(response).strip()

    except Exception as e:
        print(f"Error in generate_health_report: {e}")
        return (
            "Could not generate health report at this time.\n"
            "Please visit your nearest PHC and describe your symptoms to the doctor."
        )
