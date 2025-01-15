import datetime as dt
import requests
from typing import Dict, Any, List, Optional
import os

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org"
        
    @staticmethod
    def kelvin_to_celsius_farenheit(kelvin):
        celcius = kelvin - 273.15
        fahrenheit = celcius * (9/5) + 32
        return(celcius,fahrenheit)
    
    
    def get_weather(self , city: str) -> str:
        endpoint = f"{self.base_url}/data/2.5/weather"
        # base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            # "units": "metric"  # Use "imperial" for Fahrenheit
        }
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
           data = response.json()
           weather = data["weather"][0]["description"]
           temperature = data["main"]["temp"]
           temp_cel,temp_fah = self.kelvin_to_celsius_farenheit(temperature)
           wind = data['wind']['speed']
           cloud = data['clouds']['all']
           Humidity = data["main"]["humidity"]
           return f"Weather in {city}: {weather},Humidity: {Humidity}, Temperature: {temp_cel:.2f}°C OR {temp_fah:2f}°F, Wind: {wind}km/h, Cloud: {cloud}"
        else:
            return f"Failed to fetch weather data for {city}."




# BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast?id=524901&appid=59b8c5fa1b1e73d1c184d001c20960de'
# Geocoding_API_url = 'http://api.openweathermap.org/geo/1.0/direct?q=Pakistan&appid=59b8c5fa1b1e73d1c184d001c20960de'
# api_key="59b8c5fa1b1e73d1c184d001c20960de"
# result = get_weather("Bali",api_key)

# print(result)
