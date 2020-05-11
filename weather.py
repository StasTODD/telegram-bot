import ast
from datetime import date, datetime, timedelta
from typing import List, Dict, Union, Any
from help_functions import get_json_from_web
from aiogram.types import Location


async def get_weather_data(weather_api: str, location: Location, state: str = 'weather', lang: str = 'en') -> \
                                                                                                    Union[str, dict]:
    """
    Get API params and send request weather data to openweathermap.org
    :param weather_api: '8c4b1bbbxxxxxxxxxxxxxxxxxxx'
    :param location: <class 'aiogram.types.location.Location'>
    :param state: ['weather'|'forecast']
    :param lang: 'en|ru|...'

    :return:
    for 'weather' state:
             {'coord': {'lon': 30.51, 'lat': 50.4},
              'weather': [{'id': 500,
                'main': 'Rain',
                'description': 'light rain',
                'icon': '10d'}],
              'base': 'stations',
              'main': {'temp': 299.1,
               'feels_like': 296.27,
               'temp_min': 298.15,
               'temp_max': 300.37,
               'pressure': 1007,
               'humidity': 36},
              'visibility': 10000,
              'wind': {'speed': 4, 'deg': 200},
              'rain': {'1h': 0.12},
              'clouds': {'all': 2},
              'dt': 1589200602,
              'sys': {'type': 1,
               'id': 8903,
               'country': 'UA',
               'sunrise': 1589163360,
               'sunset': 1589218364},
              'timezone': 10800,
              'id': 703447,
              'name': 'Kyiv',
              'cod': 200}
    """
    lat = location.latitude
    lon = location.longitude
    url = f"http://api.openweathermap.org/data/2.5/{state}?lat={lat}&lon={lon}&appid={weather_api}&lang={lang}"
    data = await get_json_from_web(url)
    if data['status'] == 200 and data.get('result'):
        # Transform str -> Dict[str, str] using ast.literal_eval method:
        data = ast.literal_eval(data['result'])
        return data
    else:
        return f"Error. Get status message - {data['status']}"


async def parse_weather_api_request(weather_msg: dict) -> str:
    """
    Parse weather API request message.

    :param weather_msg:
    'forecast' API (dicts in list) return:
    {'clouds': {'all': 52},
     'dt': 1589641200,
     'dt_txt': '2020-05-16 15:00:00',
     'main': {'feels_like': 283.27,
           'grnd_level': 997,
           'humidity': 52,
           'pressure': 1015,
           'sea_level': 1015,
           'temp': 287.88,
           'temp_kf': 0,
           'temp_max': 287.88,
           'temp_min': 287.88},
     'sys': {'pod': 'd'},
     'weather': [{'description': 'broken clouds',
               'icon': '04d',
               'id': 803,
               'main': 'Clouds'}],
     'wind': {'deg': 267, 'speed': 4.97}}

    :return: parsed string
    """
    # TODO: modify API data handlers:
    kelvin = 272.15
    description = weather_msg.get('weather')[0].get('description')
    # Get temp of Kelvin and convert to the celsius:
    # temp_avg = str(round(weather_data.get('main').get('temp') - kelvin))
    temp_min = str(round(weather_msg.get('main').get('temp_min') - kelvin))
    temp_max = str(round(weather_msg.get('main').get('temp_max') - kelvin))
    atmo_pressure = str(weather_msg.get('main').get('pressure')) + 'hPa'
    humidity = str(weather_msg.get('main').get('humidity')) + '%'
    # visibility = str(weather_data.get('visibility')) + 'meters'
    wind_speed = str(weather_msg.get('wind').get('speed')) + 'm/s'
    # Wind direction, degrees (meteorological):
    # TODO: Transform wind_deg data to readable:
    # wind_deg = str(weather_data.get('wind').get('deg')) + '°'
    clouds = str(weather_msg.get('clouds').get('all')) + '%'
    set_date = weather_msg.get('dt')
    date_str = datetime.fromtimestamp(set_date).strftime("%Y %B %d, %A, %I:%M %p")
    sunrise = weather_msg.get('sys').get('sunrise')
    sunset = weather_msg.get('sys').get('sunset')
    # This 'if' need for manual split API request for 'forecast' or 'weather' call:
    if sunrise and sunset:
        sunrise = datetime.fromtimestamp(sunrise).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(sunset).strftime("%I:%M %p")
    # city = str(weather_data.get('name'))

    result_str = f'At {date_str}\n\n'\
                 f'state: {description}\n'\
                 f'temp: {temp_min}°-{temp_max}°\n' \
                 f'clouds: {clouds}\n' \
                 f'atmo pressure: {atmo_pressure}\n' \
                 f'humidity: {humidity}\n' \
                 f'wind speed: {wind_speed}'

    if sunrise and sunset:
        result_str += f'\n\nsunrise: {sunrise}\nsunset: {sunset}'

    return result_str


async def time_split_weather_message(weather_data, weather_date):
    result = []
    dates = {"/today": 0,
             "/tomorrow": 1,
             "/plus_2_days": 2,
             "/plus_3_days": 3,
             "/plus_4_days": 4}
    current_date = date.today()
    seted_date = current_date + timedelta(days=dates[weather_date])
    seted_date = seted_date.strftime('%d %B')

    for one_data in weather_data['list']:
        date_data = one_data.get('dt')
        date_data = datetime.fromtimestamp(date_data).strftime('%d %B')
        if seted_date == date_data:
            result.append(one_data)

    return result


async def create_weather_message(weather_data, weather_date: str) -> str:
    if isinstance(weather_data, str):
        return weather_data

    if weather_date == '/now':
        return await parse_weather_api_request(weather_data)
    elif weather_date in ["/today", "/tomorrow", "/plus_2_days", "/plus_3_days", "/plus_4_days"]:
        weather_data = await time_split_weather_message(weather_data, weather_date)
        # TODO: reformat reply-message to something reading
        result_msg = ""
        for one_date in weather_data:
            result_msg += await parse_weather_api_request(one_date)
            result_msg += '\n\n'
        return result_msg
    else:
        return "Error, weather message don't create"


__all__ = ['get_weather_data',
           'create_weather_message'
           ]
