def Weather_Explainer_Agent(query: str, context: dict):
    
    """
    Weather Explainer Tool

    Expects the following context:
    - place: str
    - weather_data: list
    - llm: ChatGroq

    Returns:
    - A weather explanation.
    """

    llm = context.get("llm")
    city = context.get("place")
    weather_data = context.get("weather_data")

    if not llm or not city or not weather_data:
        return "Weather information is unavailable at this time."
        
    prompt = f"""
            You are a weather explainer agent. You are given the name of the city {city}, and weather data {weather_data}. 

            The weather data is in the following format:
            - first element is current weather data
            - second element is forecast weather data

            Your task is to explain weather phenomena in simple terms so that tourists can decide if they can go to that place or not.
            Keep your explanations concise and easy to understand.
            no more than 300 words.
            Provide the following details in your explanation:
            1. Current Weather Overview: Summarize the current weather conditions, including temperature, humidity, wind speed, and any significant weather events (e.g., rain, snow, storms).
            2. Forecast Summary: Provide a brief overview of the weather forecast for the next 5 days, highlighting any notable changes or patterns.
            3. Activity Recommendations: Suggest suitable outdoor activities based on the weather conditions, such as hiking, sightseeing, beach visits, or indoor activities if the weather is unfavorable.
            4. Safety Tips: Offer any necessary safety tips related to the weather conditions, such as precautions for extreme weather, sun protection, or hydration.
            5. Packing Suggestions: Advise on what to pack for the trip based on the weather forecast, including clothing, accessories, and any special gear needed.
    """
    try:
        return llm.invoke(prompt).content
    except Exception:
        text_output = "Could not generate weather explanation at this time."
        return text_output