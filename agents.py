from langchain_groq import ChatGroq
import os

def Weather_Explainer_Agent(weatherData):

    llm = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
    prompt = f"""
    You are a weather explainer agent. You are given the current weather conditions and 5 days forecast {weatherData}. 
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

    return llm.invoke(prompt).content