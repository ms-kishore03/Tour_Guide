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
from cognix_ai.tools.hotel_tool import retieve_hotel_names as _tool_retrieve_hotel_names
load_dotenv()

def get_airport_id(city):
    llm = settings.llm
    prompt=f"""
    You are an airport code finder agent. You are given the name of the city: {city}.
    Your task is to provide the corresponding IATA airport code for the main airport in that city. No additional explanations are needed.
    """
    return llm.invoke(prompt).content.strip().upper()

def retieve_hotel_names(location, hotel_names):
    """Thin wrapper around the canonical implementation in
    cognix_ai/tools/hotel_tool.py, adapted to this module's older
    (location, hotel_names) positional calling convention."""
    return _tool_retrieve_hotel_names(
        query="", context={"place": location, "hotel_names": hotel_names, "llm": settings.llm}
    )
