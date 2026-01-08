# tools/rag_tool.py

def rag_tool(query: str, context: dict):
    """
    RAG Tool

    Expects in context:
    - rag_fn: callable (returned by load_rag())

    Returns:
    - Retrieved + generated answer from RAG
    """

    rag_fn = context.get("rag_fn")

    if not rag_fn:
        return "Knowledge base is unavailable at the moment."

    return rag_fn(query)
