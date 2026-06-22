import os
import sys

# Ensure backend directory is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.generator import get_answer

def main():
    print("--- Testing get_answer() ---")
    query = "What are the warning signs of severe dengue and what should I do?"
    print(f"Question: {query}\n")
    
    # Run the generator QA chain
    answer = get_answer(query)
    
    print("Answer:")
    print(answer)

if __name__ == "__main__":
    main()
