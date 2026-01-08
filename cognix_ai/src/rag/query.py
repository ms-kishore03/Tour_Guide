from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..")))
from config import settings

def load_rag():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=settings.VECTOR_DB_DIR,
        embedding_function=embeddings
    )

    retriever = db.as_retriever(search_kwargs={"k": 5})

    llm = settings.llm

    def ask(query: str):
        docs = retriever.invoke(query)

        context = "\n\n".join(
            f"[{d.metadata.get('title')} - {d.metadata.get('section')}]\n{d.page_content}"
            for d in docs
        )

        prompt = f"""
You are a travel assistant.
Use ONLY the context below to answer.

Context:
{context}

Question:
{query}
"""
        return llm.invoke(prompt).content

    return ask
