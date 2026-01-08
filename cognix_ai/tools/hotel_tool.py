def retieve_hotel_names(query: str, context: dict):

    """
    Hotel Name Retriever Tool

    Expects the following context:
    - place: str
    - hotel_names: str
    - llm: ChatGroq

    Returns:
    - A cleaned list of hotel names.
    """

    llm = context.get("llm")
    location = context.get("place")
    hotel_names = context.get("hotel_names")

    if not llm or not location or not hotel_names:
        return "Hotel information is unavailable at this time."

    prompt = f"""
        You are given raw hotel names from {location}.

        TASK:
        - Remove any extra descriptors or suffixes
        - Keep ONLY the clean hotel name

        OUTPUT FORMAT (MANDATORY):
        Return ONLY a numbered list.
        Each line must be: <number>. <hotel name>
        No explanations.
        No arrows.
        No extra text.
        No headings.

        INPUT:
        {hotel_names}
    """
    return llm.invoke(prompt).content.strip()