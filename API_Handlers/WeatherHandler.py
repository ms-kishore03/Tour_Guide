import requests
from dotenv import load_dotenv
import os

load_dotenv(".env")
API_Key = os.getenv("OpenWeatherMap_API_Key")

def get_coordinates(city):
    limit = 1

    get_geographical_coordinates = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={limit}&appid={API_Key}"

    geo_res = requests.get(get_geographical_coordinates).json()
    lat = geo_res[0]["lat"]
    lon = geo_res[0]["lon"]
    return lat, lon

def current_weather_info(city):
    lat,lon = get_coordinates(city)
    
    get_climate_values = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_Key}"

    climate_res = requests.get(get_climate_values).json()

    return(
        f"The weather is:", {climate_res['weather'][0]['description']},
        f"and the temperature is:", {climate_res['main']['temp']}, "K.",
        f"The humidity is:", {climate_res['main']['humidity']}, "%.",
        f"The max temperature is:", {climate_res['main']['temp_max']}, "K,",
        f"and the min temperature is:", {climate_res['main']['temp_min']}, "K.",
        f"The latitude is:", {lat},
        f"and the longitude is:", {lon}
    )

def forecast_weather_info(city):

    lat, lon = get_coordinates(city)
    get_forecast_values = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_Key}"

    forecast_res = requests.get(get_forecast_values).json()

    forecast_list = []
    for forecast in forecast_res['list']:
        forecast_list.append(
            {
                "datetime": forecast['dt_txt'],
                "temperature": forecast['main']['temp'],
                "weather": forecast['weather'][0]['description'],
                "humidity": forecast['main']['humidity']
            }
        )
    
    return forecast_list