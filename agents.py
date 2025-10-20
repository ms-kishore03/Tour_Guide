from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
def Weather_Explainer_Agent(current_data,forecast_data):

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    validation = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= f"""
            You are a weather explainer agent. You are given the current weather conditions {current_data} and 5 days forecast {forecast_data}. 
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

    )
    try:
        text_output = validation.candidates[0].content.parts[0].text.strip()
        return text_output
    except Exception as e:
        text_output = "Could not generate weather explanation at this time."
        return text_output


def enquiry_agent_chatbot(conversation_history,user_input,weather_info):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    conversation = ""
    for message in conversation_history:
        role = message['role']
        content = message['content']
        conversation += f"{role}: {content}\n"
    conversation += f"user: {user_input}\nassistant:"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= f"""You are a friendly travel chatbot assisting tourists.
                You have access to weather details: {weather_info} and past conversation: {conversation}.
                Use these as helpful context, but you can also draw on your own general travel knowledge when needed.
                If certain details (like entry fees, timings, or local tips) aren't in the given info, provide reasonable estimates or widely known facts — 
                but make it sound natural, as if chatting with a traveler.
                Keep replies under 100 words, conversational, and easy to follow."""
    )
    try:
        text_output = response.candidates[0].content.parts[0].text.strip()
        return text_output
    except Exception as e:
        text_output = "Could not generate a response at this time."
        return text_output
    
def get_attractive_points(destination):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= f"""You are a travel guide agent. You are given a destination: {destination}. 
            Your task is to provide a list of top 10 attractive points of interest for tourists visiting this destination.
            Just provide the list without any additional explanations."""
    )
    try:
        text_output = response.candidates[0].content.parts[0].text.strip()
        return text_output
    except Exception as e:
        text_output = "Could not generate attractive points at this time."
        return text_output