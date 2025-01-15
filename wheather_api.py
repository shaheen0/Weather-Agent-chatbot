import requests
import os
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv() 

@dataclass
class WeatherData:
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    description: str
    wind_speed: float
    clouds: int
    rain_chance: float

class WeatherAPI:
    def __init__(self, api_key: str):
        """
        Initialize Weather API client
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"

    def _get_coordinates(self, city: str) -> Optional[tuple]:
        """
        Get latitude and longitude for a city
        Args:
            city: City name
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            params = {
                'q': city,
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(self.geo_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return (data[0]['lat'], data[0]['lon'])
            return None
            
        except Exception as e:
            print(f"Error getting coordinates: {str(e)}")
            return None

    def get_current_weather(self, city: str) -> Optional[WeatherData]:
        """
        Get current weather for a city
        Args:
            city: City name
        Returns:
            WeatherData object or None if error
        """
        try:
            # First get coordinates
            coords = self._get_coordinates(city)
            if not coords:
                return None
                
            lat, lon = coords
            
            # Get weather data
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius
            }
            
            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return WeatherData(
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                temp_min=data['main']['temp_min'],
                temp_max=data['main']['temp_max'],
                humidity=data['main']['humidity'],
                description=data['weather'][0]['description'],
                wind_speed=data['wind']['speed'],
                clouds=data['clouds']['all'],
                rain_chance=data.get('rain', {}).get('1h', 0)
            )
            
        except Exception as e:
            print(f"Error getting weather: {str(e)}")
            return None

    def get_forecast(self, city: str, days: int = 5) -> Optional[Dict]:
        """
        Get weather forecast for a city
        Args:
            city: City name
            days: Number of days (max 5 for free tier)
        Returns:
            Dictionary with forecast data or None if error
        """
        try:
            # First get coordinates
            coords = self._get_coordinates(city)
            if not coords:
                return None
                
            lat, lon = coords
            
            # Get forecast data
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # API returns data in 3-hour increments
            }
            
            response = requests.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process and organize forecast data by day
            forecasts = {}
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                
                if date not in forecasts:
                    forecasts[date] = {
                        'temp_min': float('inf'),
                        'temp_max': float('-inf'),
                        'humidity': [],
                        'descriptions': set(),
                        'wind_speed': [],
                        'rain_chance': []
                    }
                
                forecast = forecasts[date]
                forecast['temp_min'] = min(forecast['temp_min'], item['main']['temp_min'])
                forecast['temp_max'] = max(forecast['temp_max'], item['main']['temp_max'])
                forecast['humidity'].append(item['main']['humidity'])
                forecast['descriptions'].add(item['weather'][0]['description'])
                forecast['wind_speed'].append(item['wind']['speed'])
                forecast['rain_chance'].append(item.get('pop', 0) * 100)  # Convert to percentage
            
            # Calculate averages for each day
            for date in forecasts:
                forecasts[date]['humidity'] = sum(forecasts[date]['humidity']) / len(forecasts[date]['humidity'])
                forecasts[date]['wind_speed'] = sum(forecasts[date]['wind_speed']) / len(forecasts[date]['wind_speed'])
                forecasts[date]['rain_chance'] = sum(forecasts[date]['rain_chance']) / len(forecasts[date]['rain_chance'])
            
            return forecasts
            
        except Exception as e:
            print(f"Error getting forecast: {str(e)}")
            return None

def check_weather(location_info: str) -> Dict:
    """
    Main function to check weather (matches the tool calling pattern)
    Format: city,date
    Example: check_weather:London,2024-06
    """
    try:
        # Parse input
        city, date = location_info.split(',')
        
        # Get API key from environment
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable not set")
        
        # Initialize API client
        client = WeatherAPI(api_key)
        
        # Get current weather and forecast
        current = client.get_current_weather(city)
        forecast = client.get_forecast(city)
        
        return {
            'current': {
                'temperature': current.temperature if current else None,
                'description': current.description if current else None,
                'humidity': current.humidity if current else None,
                'wind_speed': current.wind_speed if current else None
            },
            'forecast': forecast
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

# Example usage
if __name__ == "__main__":
    # Set up your environment variable first:
    # export OPENWEATHER_API_KEY='your_api_key'
    api_key = os.getenv('WEATHER_API_KEY')
    weather_api = WeatherAPI(api_key)
    # Test the weather check
    weather_info = check_weather("Pakistan,2025-02")
    
    # Print current weather
    if weather_info.get('current'):
        print("\nCurrent Weather:")
        print(f"Temperature: {weather_info['current']['temperature']}°C")
        print(f"Description: {weather_info['current']['description']}")
        print(f"Humidity: {weather_info['current']['humidity']}%")
        print(f"Wind Speed: {weather_info['current']['wind_speed']} m/s")
    
    # # Print forecast
    # if weather_info.get('forecast'):
    #     print("\nForecast:")
    #     for date, data in weather_info['forecast'].items():
    #         print(f"\n{date}:")
    #         print(f"Temperature: {data['temp_min']:.1f}°C to {data['temp_max']:.1f}°C")
    #         print(f"Humidity: {data['humidity']:.0f}%")
    #         print(f"Wind Speed: {data['wind_speed']:.1f} m/s")
    #         print(f"Rain Chance: {data['rain_chance']:.0f}%")
    #         print(f"Conditions: {', '.join(data['descriptions'])}")