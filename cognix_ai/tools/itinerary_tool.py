# cognix_ai/tools/itinerary_tool.py

def Itinerary_Agent(query: str, context: dict):
    """
    Handles FINALIZATION of itinerary only.
    Assumes draft is already correct.
    """

    collection = context.get("collection")
    username = context.get("username")
    place = context.get("place")
    draft = context.get("draft_itinerary")

    # ---------- SAFE CHECKS ----------
    if collection is None:
        return "Database connection unavailable."

    if not username or not place:
        return "User or destination missing."

    if not isinstance(draft, list) or not draft:
        return "No itinerary to save."

    # ---------- NORMALIZE DATA ----------
    itinerary_list = []
    for item in draft:
        itinerary_list.append({
            "location": item.get("location"),
            "date": item.get("date", "unknown"),
            "time": item.get("time", "unknown")
        })

    # ---------- UPSERT ----------
    collection.update_one(
        {
            "username": username,
            "place": place
        },
        {
            "$set": {
                "username": username,
                "place": place,
                "itinerary_list": itinerary_list
            }
        },
        upsert=True
    )

    return "Your itinerary has been finalized and saved successfully."
