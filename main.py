from openwheatherapi import WeatherAPI
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    weather_api = WeatherAPI(api_key)
    result = weather_api.get_weather("Bahawalpur",api_key)
    print(result)