import os
import sys

# Ensure backend directory is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.retriever import build_index, get_retriever, retrieve_documents

def main():
    print("--- Testing build_index() ---")
    build_index()
    
    print("\n--- Testing get_retriever() ---")
    retriever = get_retriever()
    print("Retriever obtained successfully:", retriever)
    
    print("\n--- Testing retrieve_documents() for 'dengue symptoms' ---")
    results = retrieve_documents("What are the warning signs of severe dengue?", limit=2)
    for i, doc in enumerate(results):
        print(f"\nResult {i+1} (Source: {doc['metadata'].get('source')}):")
        print(doc['page_content'])

if __name__ == "__main__":
    main()
