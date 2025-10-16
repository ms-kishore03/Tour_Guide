import Utilities.User_Authentication as User_Authentication
from API_Handlers import WeatherHandler
import agents


action = input("Do you want to (1) Register or (2) Login? ")
if action == '1':
    username = input("Enter username: ")
    password = input("Enter password: ")
    confirm_password = input("Confirm password: ")
    email = input("Enter email: ")
    print(User_Authentication.register(username, password, confirm_password, email))
    
elif action == '2':
    username = input("Enter username: ")
    password = input("Enter password: ")
    login = User_Authentication.login(username, password)

    if login:
        weatherData = []
        city = input("Enter city name for weather information: ")
        weatherData.append(WeatherHandler.current_weather_info(city))
        forecast = WeatherHandler.forecast_weather_info(city)
        for day in forecast:
            weatherData.append(day)

        print("========== Weather Explanation ==========")
        explanation = agents.Weather_Explainer_Agent(weatherData)
        print(explanation)