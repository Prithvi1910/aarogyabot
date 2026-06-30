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

# Chat model is configurable; default to a stronger model for better medical accuracy.
CHAT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def get_llm():
    """
    Loads GROQ_API_KEY from environment.
    Returns a ChatGroq instance using the configured CHAT_MODEL (default
    "llama-3.3-70b-versatile") with temperature 0.2.
    If GROQ_API_KEY is not set, falls back to Ollama with model "llama3.2".
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key.strip():
        return ChatGroq(
            model=CHAT_MODEL,
            temperature=0.2,
            groq_api_key=groq_api_key.strip()
        )
    else:
        return Ollama(
            model="llama3.2",
            temperature=0.2
        )

HEALTH_PROMPT = PromptTemplate.from_template(
    "You are AarogyaBot, a careful and trustworthy public health assistant for rural India.\n"
    "Use ONLY the information in the provided context to answer. If the context does not contain "
    "the answer, say you are not certain and advise visiting the nearest Primary Health Centre (PHC) "
    "— never guess or invent medical facts, conditions, or medicines.\n"
    "Write in simple, clear language that a person with little schooling can understand. "
    "Keep it short: 2 to 4 short sentences.\n"
    "When the context supports it, include: (a) the most likely cause, (b) one or two safe home-care "
    "steps, and (c) one clear red-flag sign that means they must see a doctor.\n\n"
    "MEDICINE SAFETY RULES:\n"
    "- You MAY name common over-the-counter remedies for mild symptoms when the context supports them "
    "(e.g. Paracetamol for fever, ORS for dehydration/diarrhoea, antiseptic for minor wounds, "
    "Oral Rehydration Salts for fluid loss).\n"
    "- NEVER prescribe antibiotics, antimalarials, or other prescription drugs, and NEVER give specific "
    "prescription dosages. For anything stronger, say: 'please consult a doctor at your nearest PHC'.\n"
    "- For dengue or suspected dengue, recommend ONLY Paracetamol and warn against Aspirin and Ibuprofen.\n"
    "- NEVER say you cannot help — always give the safe step first, then refer to a PHC if needed.\n"
    "- Do not repeat the exact same phrasing every time; vary your wording.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
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

def _pretty_source(filename: str) -> str:
    """Turn a doc filename like 'snake_bite_emergency.txt' into 'Snake Bite Emergency'."""
    name = filename.rsplit(".", 1)[0].replace("_", " ").strip()
    return name.title()


def get_answer_with_sources(query: str, history: list = []) -> Dict[str, Any]:
    """
    Same as get_answer_with_history, but also returns the health-doc sources the
    answer was grounded in, for transparency / anti-hallucination citations.
    Returns {"answer": str, "sources": [str, ...]}.
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        context_str = "\n\n".join([doc.page_content for doc in docs])

        # Placeholder/sample docs that should not be cited to the user
        SKIP_SOURCES = {"sample_health.txt"}
        sources = []
        for doc in docs:
            src = doc.metadata.get("source")
            if src and src not in SKIP_SOURCES:
                pretty = _pretty_source(src)
                if pretty not in sources:
                    sources.append(pretty)

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
        answer = response.content.strip() if hasattr(response, "content") else str(response).strip()
        return {"answer": answer, "sources": sources[:3]}
    except Exception as e:
        print(f"Error in get_answer_with_sources: {e}")
        return {
            "answer": "I am sorry, I am having trouble answering right now. Please visit your nearest PHC.",
            "sources": [],
        }


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
            model=CHAT_MODEL,
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
