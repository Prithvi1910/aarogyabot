# After adding new health docs, delete data/faiss_index/ and run build_index() to rebuild
import os
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Paths relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
DOCS_DIR = os.path.join(BACKEND_DIR, "data", "health_docs")
FAISS_DIR = os.path.join(BACKEND_DIR, "data", "faiss_index")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build_index():
    """
    Reads all .txt files from backend/data/health_docs/
    Splits them into chunks of 500 characters with 50 overlap using RecursiveCharacterTextSplitter
    Embeds using HuggingFaceEmbeddings with model "sentence-transformers/all-MiniLM-L6-v2"
    Saves FAISS index to backend/data/faiss_index/
    Prints how many chunks were indexed
    """
    os.makedirs(FAISS_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    documents = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                documents.append(Document(page_content=text, metadata={"source": filename}))
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")
                
    if not documents:
        print("No documents found in health_docs/ directory to index.")
        return

    # Larger chunks keep each condition's full entry (cause, home care, red flags,
    # medicine) together, which improves retrieval accuracy for medical Q&A.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(FAISS_DIR)
    
    print(f"Indexed {len(chunks)} chunks from {len(documents)} document(s).")

def get_retriever():
    """
    Loads the saved FAISS index using the same embedding model
    Returns a retriever with k=5 and score_threshold=0.45
    If index does not exist, calls build_index() first automatically
    """
    faiss_file = os.path.join(FAISS_DIR, "index.faiss")
    if not os.path.exists(faiss_file):
        print("FAISS index files not found. Initiating index build...")
        build_index()
        
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6}
    )

def retrieve_documents(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Queries vector database or search index for matching health docs.
    """
    try:
        retriever = get_retriever()
        # Optionally override search_kwargs if limit is customized
        if limit != 5:
            retriever.search_kwargs["k"] = limit
        docs = retriever.invoke(query)
        return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []
