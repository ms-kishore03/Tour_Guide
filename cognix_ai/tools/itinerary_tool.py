def Itinerary_Agent(query: str, context: dict):
    """
    Stores multi-day itinerary grouped by date.
    """

    collection = context.get("collection")
    username = context.get("username")
    place = context.get("place")
    itinerary = context.get("draft_itinerary")

    if collection is None or not username or not place:
        return "Database unavailable."

    if not itinerary:
        return "No itinerary to save."

    # Group by date
    grouped = {}
    for item in itinerary:
        date = item["date"]
        grouped.setdefault(date, []).append({
            "location": item["location"],
            "time": item["time"]
        })

    doc = {
        "username": username,
        "place": place,
        "itinerary_by_date": grouped
    }

    collection.update_one(
        {"username": username, "place": place},
        {"$set": doc},
        upsert=True
    )


    return "Your multi-day itinerary has been saved successfully."
