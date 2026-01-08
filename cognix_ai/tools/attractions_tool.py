def select_top_attractions(query: str, context: dict):
    """
    Attraction Selector Tool

    Expects in context:
    - place: str
    - geoapify_data: list
    - llm: ChatGroq

    Returns:
    - list[str]  (EXACTLY 10 clean attraction names)
    """

    place = context.get("place")
    geoapify_data = context.get("geoapify_data")
    llm = context.get("llm")

    if not place or not geoapify_data or not llm:
        return []

    prompt = f"""
You are a travel expert.

Select EXACTLY 10 REAL tourist attractions for {place}.

RULES:
- Output ONLY names
- One per line
- NO numbering
- NO explanations
- NO sentences

RAW DATA:
{geoapify_data}
"""

    try:
        response = llm.invoke(prompt).content.strip()

        attractions = [
            line.strip()
            for line in response.split("\n")
            if line.strip()
        ]

        # 🔒 HARD SAFETY
        if not isinstance(attractions, list):
            return []

        return attractions[:10]

    except Exception:
        return []
