from google import genai
from google.genai import errors
from langchain_groq import ChatGroq
import time
import os
from dotenv import load_dotenv
import re
import json
load_dotenv()

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
    
    prompt = f"""
    You are a travel guide agent. You are given a destination: {destination}. 
    Your task is to provide a list of top 10 attractive points of interest for tourists visiting this destination.
    Return only the names of places as a simple numbered list, one per line.
    """

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text_output = response.candidates[0].content.parts[0].text.strip()
            lines = [
                line.strip().lstrip("0123456789.-) ").strip()
                for line in text_output.split("\n")
                if line.strip()
            ]
            return lines

        except errors.ServerError as e:
            if e.code == 503:  # Model overloaded
                wait_time = (2 ** attempt) + 1
                print(f"⚠️ Gemini model overloaded. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                raise  # Other server error, re-raise

        except Exception as e:
            print(f"⚠️ Error in get_attractive_points: {e}")
            break

    # Fallback to a smaller, more stable model
    try:
        print("⚙️ Falling back to gemini-1.0-pro...")
        response = client.models.generate_content(
            model="gemini-1.0-pro",
            contents=prompt
        )
        text_output = response.candidates[0].content.parts[0].text.strip()
        lines = [
            line.strip().lstrip("0123456789.-) ").strip()
            for line in text_output.split("\n")
            if line.strip()
        ]
        return lines

    except Exception as e:
        print(f"❌ Final fallback failed: {e}")
        return ["Could not generate attractive points at this time."]


def chatbot(conversation_history,user_input,weather_info):
    llm = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
    
    conversation = ""
    for message in conversation_history:
        role = message['role']
        content = message['content']
        conversation += f"{role}: {content}\n"
    conversation += f"user: {user_input}\nassistant:"

    prompt = f"""
                You are a friendly travel chatbot assisting tourists.
                You have access to weather details: {weather_info} and past conversation: {conversation}.
                Use these as helpful context, but you can also draw on your own general travel knowledge when needed.
                If certain details (like entry fees, timings, or local tips) aren't in the given info, provide reasonable estimates or widely known facts — 
                but make it sound natural, as if chatting with a traveler.
                Keep replies under 100 words, conversational, and easy to follow.
    
    """
    return llm.invoke(prompt).content

def Weather_Explainer_Agent(city,current_data,forecast_data):

    llm = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
    
    prompt = f"""
    You are a weather explainer agent. You are given the name of the city {city}, current weather conditions {current_data} and 5 days forecast {forecast_data}. 
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
    except Exception as e:
        text_output = "Could not generate weather explanation at this time."
        return text_output
    
def get_airport_id(city):
    llm = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
    prompt=f"""
    You are an airport code finder agent. You are given the name of the city: {city}. 
    Your task is to provide the corresponding IATA airport code for the main airport in that city. No additional explanations are needed.
    """
    return llm.invoke(prompt).content.strip().upper()