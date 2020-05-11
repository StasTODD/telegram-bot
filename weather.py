import ast
from datetime import datetime
from typing import List, Dict, Union, Any
from help_functions import get_json_from_web


async def get_weather_data(weather_api, location, lang='en'):
    lat = location.latitude
    lon = location.longitude
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api}&lang={lang}"
    data = await get_json_from_web(url)
    if data['status'] == 200 and data.get('result'):
        # Transform str -> Dict[str, str] using ast.literal_eval method:
        data = ast.literal_eval(data['result'])
        return data
    else:
        return f"Error. Get status message - {data['status']}"


async def create_weather_message(weather_data):
    kelvin = 272.15
    if isinstance(weather_data, str):
        return weather_data
    else:
        description = weather_data.get('weather')[0].get('description')
        # Get temp of Kelvin and convert to the celsius:
        temp_avg = str(round(weather_data.get('main').get('temp') - kelvin))
        temp_min = str(round(weather_data.get('main').get('temp_min') - kelvin))
        temp_max = str(round(weather_data.get('main').get('temp_max') - kelvin))
        atmo_pressure = str(weather_data.get('main').get('pressure')) + 'hPa'
        humidity = str(weather_data.get('main').get('humidity')) + '%'
        visibility = str(weather_data.get('visibility')) + 'meters'
        wind_speed = str(weather_data.get('wind').get('speed')) + 'm/s'
        # Wind direction, degrees (meteorological):
        # TODO: Transform wind_deg data to readable:
        wind_deg = str(weather_data.get('wind').get('deg')) + '°'
        clouds = str(weather_data.get('clouds').get('all')) + '%'
        date = weather_data.get('dt')
        date_str = datetime.fromtimestamp(date).strftime("%Y %B %d, %A, %I:%M %p")
        sunrise = weather_data.get('sys').get('sunrise')
        sunrise = datetime.fromtimestamp(sunrise).strftime("%I:%M %p")
        sunset = weather_data.get('sys').get('sunset')
        sunset = datetime.fromtimestamp(sunset).strftime("%I:%M %p")
        city = str(weather_data.get('name'))

        weather_now = f'At this moment:\n' \
                      f'{date_str}\n\n' \
                      f'state: {description}\n' \
                      f'temp: {temp_avg}°\n' \
                      f'temp period: {temp_min}°-{temp_max}°\n' \
                      f'clouds: {clouds}\n' \
                      f'atmo pressure: {atmo_pressure}\n' \
                      f'humidity: {humidity}\n' \
                      f'wind speed: {wind_speed}\n' \
                      f'visibility: {visibility}\n\n' \
                      f'nearest city: {city}\n' \
                      f'sunrise: {sunrise}\n' \
                      f'sunset: {sunset}'
        return weather_now


__all__ = ['get_weather_data',
           'create_weather_message'
           ]
