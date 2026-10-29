import requests

API_KEY_PARAM = "api_key"
WEATHER_URL = "https://api.weather.example/v1/current"


def current_weather(city, key):
    return requests.get(WEATHER_URL, params={"q": city, API_KEY_PARAM: key}, timeout=5).json()
