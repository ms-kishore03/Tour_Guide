import requests
from dotenv import load_dotenv
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import agents
load_dotenv(".env")
API_Key = os.getenv("OpenWeatherMap_API_Key")

def current_weather_info(lat,lon,city):
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_Key}"
    res = requests.get(url).json()

    if "weather" not in res:
        return f"Could not retrieve weather for {city}. Response: {res}"

    return (
        f"The weather in {city} is {res['weather'][0]['description']} with "
        f"temperature {res['main']['temp']} K, humidity {res['main']['humidity']}%, "
        f"max {res['main']['temp_max']} K, min {res['main']['temp_min']} K. "
        f"(lat: {lat}, lon: {lon})"
    )


def forecast_weather_info(lat,lon,city):

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_Key}"
    res = requests.get(url).json()

    if "list" not in res:
        return f"Could not retrieve forecast for {city}. Response: {res}"

    return [
        {
            "datetime": f["dt_txt"],
            "temperature": f["main"]["temp"],
            "weather": f["weather"][0]["description"],
            "humidity": f["main"]["humidity"],
        }
        for f in res["list"]
    ]

def Weather_Explainer(lat,long,city):
    current_data = current_weather_info(lat,long,city)
    forecast_data = forecast_weather_info(lat,long,city)
    print(current_data)
    print(forecast_data)
    explanation = agents.Weather_Explainer_Agent(current_data,forecast_data)
    return explanation


print(Weather_Explainer(10.0869959,77.0600915,"Munnar"))