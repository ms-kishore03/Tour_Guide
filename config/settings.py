import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_groq import ChatGroq
from google import genai

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant",temperature=0)
DATA_PATH = "data/wikivoyage_chunks.jsonl"
VECTOR_DB_DIR = "vectorstore/chroma"
mongo_db_client = MongoClient(os.getenv("MONGODB_URI"))
gemini_llm = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
