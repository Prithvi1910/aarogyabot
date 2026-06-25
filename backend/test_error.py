import os
import uuid
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from pipeline.generator import get_llm, HEALTH_PROMPT, SESSION_MEMORIES
from pipeline.retriever import get_retriever

def test():
    llm = get_llm()
    retriever = get_retriever()
    session_id = str(uuid.uuid4())
    SESSION_MEMORIES[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    memory = SESSION_MEMORIES[session_id]

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": HEALTH_PROMPT}
    )

    response = qa_chain.invoke({"question": "I am feeling sleepy and tired"})
    print("Response:", response)

if __name__ == "__main__":
    test()
