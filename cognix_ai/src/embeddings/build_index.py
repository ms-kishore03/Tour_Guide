import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.adapter.jsonl_adapter import load_documents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..")))
from config.settings import VECTOR_DB_DIR
import shutil
import os

if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

def build_index():
    docs = load_documents()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    texts = [d["content"] for d in docs]
    metadatas = [d["metadata"] for d in docs]

    db = Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    db.persist()
    print(f"Vector DB built with {len(texts)} documents")

if __name__ == "__main__":
    build_index()
