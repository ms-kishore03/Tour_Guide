from google import genai
from google.genai import errors
from langchain_groq import ChatGroq
import time
import os
from dotenv import load_dotenv
import re
import json
from config import settings
import API_Handlers.geoapify as geoapify
load_dotenv()

def get_airport_id(city):
    llm = settings.llm
    prompt=f"""
    You are an airport code finder agent. You are given the name of the city: {city}. 
    Your task is to provide the corresponding IATA airport code for the main airport in that city. No additional explanations are needed.
    """
    return llm.invoke(prompt).content.strip().upper()

def retieve_hotel_names(location,hotel_names):
    llm = settings.llm
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
