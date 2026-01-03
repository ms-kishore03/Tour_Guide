from google import genai
from google.genai import errors
from langchain_groq import ChatGroq
import time
import os
from dotenv import load_dotenv
import re
import json
import API_Handlers.geoapify as geoapify
load_dotenv()

def enquiry_agent_chatbot(conversation_history,user_input,weather_info,place,attractive_points):
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

            Destination: {place}

            Context you can use:
            - Suggested attractions in {place}: {', '.join(attractive_points)}
            - Current weather details: {weather_info}
            - Previous conversation: {conversation}

            Instructions:
            - Answer like a helpful local travel guide.
            - When mentioning attractions, briefly explain why tourists enjoy them.
            - Use the provided attractions first, but you may add well-known ones if relevant.
            - If you genuinely don’t know something about the place, say so politely.
            - If details like timings or fees are missing, give reasonable, commonly known estimates.
            - Keep responses conversational, natural, and under 100 words.
        """
    )
    try:
        text_output = response.candidates[0].content.parts[0].text.strip()
        return text_output
    except Exception as e:
        text_output = "Could not generate a response at this time."
        return text_output

def select_top_attractions(destination, geoapify_data):
    client = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
    prompt = f"""
        You are a travel planning agent.

        Destination: {destination}

        You are given a list of candidate places extracted from a map API.
        Some entries may be:
        - duplicates
        - misleading names
        - roads, viewpoints without tourist value
        - overly similar places (same attraction, different naming)

        Your tasks:
        1. Deduplicate places referring to the same real-world attraction.
        2. Remove places that are not genuine tourist attractions.
        3. Select the BEST and MOST RELEVANT places.
        4. If fewer than 10 high-quality unique attractions remain,
        intelligently add well-known attractions of this destination
        using your general knowledge.
        5. Ensure the final output has EXACTLY 10 UNIQUE attractions.

        Candidate places (JSON):
        {geoapify_data}

        Output format:
        A list of 10 attraction names only.
        No explanations. No numbers. No extra text.
        Just a list of names.
    """

    return client.invoke(prompt).content.strip().split("\n")

def get_attractive_points(destination):
    geo_data = geoapify.geoapify_attractions(destination)
    return select_top_attractions(destination,geo_data)

def chatbot(conversation_history,user_input,weather_info,place,attractive_points):
    llm = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
    
    conversation = ""
    for message in conversation_history:
        role = message['role']
        content = message['content']
        conversation += f"{role}: {content}\n"
    conversation += f"user: {user_input}\nassistant:"

    prompt = f"""
                You are a friendly travel chatbot assisting tourists.
                The place being discussed is {place}.
                Here are some attractive points of interest in {place}: {', '.join(attractive_points)}. Keep in mind these places while answering and these are suggested by you. So while answering try explaining why these places are attractive to tourists.
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

def retieve_hotel_names(location,hotel_names):
    llm = ChatGroq(groq_api_key=os.getenv("GROG_API_KEY"), model_name="llama-3.3-70b-versatile")
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
