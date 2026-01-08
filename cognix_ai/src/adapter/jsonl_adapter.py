import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..")))
from config.settings import DATA_PATH

def load_documents():
    """
    Adapts existing Wikivoyage JSONL into RAG-ready documents.
    """

    documents = []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)

            content = obj.get("text", "").strip()
            if not content:
                continue

            metadata = {
                "source": obj.get("source"),
                "title": obj.get("title"),
                "section": obj.get("section"),
                "license": obj.get("license"),
            }

            documents.append({
                "content": content,
                "metadata": metadata
            })

    return documents
