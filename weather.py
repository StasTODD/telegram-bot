import ast
from datetime import date, datetime, timedelta
from typing import List, Dict, Union, Any
from help_functions import get_json_from_web
from aiogram.types import Location


async def get_weather_data(weather_api: str, location: Location, state: str = "weather", lang: str = "en") -> \
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
    if data["status"] == 200 and data.get("result"):
        # Transform str -> Dict[str, str] using ast.literal_eval method:
        data = ast.literal_eval(data["result"])
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
    kelvin = 272.15
    description = weather_msg.get("weather")[0].get("description")
    # Get temp of Kelvin and convert to the celsius:
    # temp_avg = str(round(weather_data.get("main").get("temp") - kelvin))
    temp_min = str(round(weather_msg.get("main").get("temp_min") - kelvin))
    temp_max = str(round(weather_msg.get("main").get("temp_max") - kelvin))
    atmo_pressure = str(weather_msg.get("main").get("pressure")) + "hPa"
    humidity = str(weather_msg.get("main").get("humidity")) + "%"
    # visibility = str(weather_data.get("visibility")) + "meters"
    wind_speed = str(weather_msg.get("wind").get("speed")) + "m/s"
    # Wind direction, degrees (meteorological):
    # TODO: Transform wind_deg data to readable:
    # wind_deg = str(weather_data.get("wind").get("deg")) + "°"
    clouds = str(weather_msg.get("clouds").get("all")) + "%"
    set_date = weather_msg.get("dt")
    date_str = datetime.fromtimestamp(set_date).strftime("%Y %B %d, %A, %I:%M %p")
    sunrise = weather_msg.get("sys").get("sunrise")
    sunset = weather_msg.get("sys").get("sunset")
    # This 'if' need for manual split API request for 'forecast' or 'weather' call:
    if sunrise and sunset:
        sunrise = datetime.fromtimestamp(sunrise).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(sunset).strftime("%I:%M %p")
    # city = str(weather_data.get('name'))

    if temp_min == temp_max:
        temp_str = temp_min + "°"
    else:
        temp_str = f"{temp_min}°-{temp_max}°"

    result_str = f"At {date_str}\n\n"\
                 f"state: {description}\n"\
                 f"temp: {temp_str}\n" \
                 f"clouds: {clouds}\n" \
                 f"atmo pressure: {atmo_pressure}\n" \
                 f"humidity: {humidity}\n" \
                 f"wind speed: {wind_speed}"

    if sunrise and sunset:
        result_str += f"\nsunrise: {sunrise}\nsunset: {sunset}"

    return result_str


async def time_split_weather_message(weather_data: Dict[str, Union[int, dict, str, list]], weather_date: str) -> \
                                                                            List[Dict[str, Union[int, dict, str, list]]]:
    """
    Got from API weather-data and split it to time. Returned date-parsed weather data.

    :param weather_data: {'list': [{'wether': 'data'}, {'wether': 'data'}, ...]}
    :param weather_date: one from:
                         ["/today", "/tomorrow", "/plus_2_days", "/plus_3_days", "/plus_4_days""]
    :return: [{'dt': 1589727600,
               'main': {'temp': 287.12,
                'feels_like': 283.01,
                'temp_min': 286.09,
                'temp_max': 287.12,
                'pressure': 1017,
                'sea_level': 1016,
                'grnd_level': 998,
                'humidity': 69,
                'temp_kf': 1.03},
               'weather': [{'id': 500,
                 'main': 'Rain',
                 'description': 'light rain',
                 'icon': '10d'}],
               'clouds': {'all': 98},
               'wind': {'speed': 5.34, 'deg': 213},
               'rain': {'3h': 0.46},
               'sys': {'pod': 'd'},
               'dt_txt': '2020-05-17 15:00:00'},
              {'dt': 1589738400,
               'main': {'temp': 284.03,
                'feels_like': 281.43,
                'temp_min': 283.56,
                'temp_max': 284.03,
                'pressure': 1016,
                'sea_level': 1016,
                'grnd_level': 998,
                'humidity': 81,
                'temp_kf': 0.47},
               'weather': [{'id': 500,
                 'main': 'Rain',
                 'description': 'light rain',
                 'icon': '10n'}],
               'clouds': {'all': 94},
               'wind': {'speed': 2.97, 'deg': 239},
               'rain': {'3h': 0.24},
               'sys': {'pod': 'n'},
               'dt_txt': '2020-05-17 18:00:00'}]
    """
    result = []
    dates = {"/today": 0,
             "/tomorrow": 1,
             "/plus_2_days": 2,
             "/plus_3_days": 3,
             "/plus_4_days": 4}
    current_date = date.today()
    seted_date = current_date + timedelta(days=dates[weather_date])
    seted_date = seted_date.strftime("%d %B")

    for one_data in weather_data["list"]:
        date_data = one_data.get("dt")
        date_data = datetime.fromtimestamp(date_data).strftime("%d %B")
        if seted_date == date_data:
            result.append(one_data)

    return result


async def create_weather_message(weather_data: Dict[str, Union[dict, list, str, int]], weather_date: str) -> str:
    """
    Got API-data, call parse functions and return readable string.

    :param weather_data: For example, '/now' string:
                          {'coord': {'lon': 30.51, 'lat': 50.4},
                          'weather': [{'id': 500,
                            'main': 'Rain',
                            'description': 'light rain',
                            'icon': '10d'}],
                          'base': 'stations',
                          'main': {'temp': 290.7,
                           'feels_like': 285.87,
                           'temp_min': 290.15,
                           'temp_max': 292.15,
                           'pressure': 1019,
                           'humidity': 51},
                          'visibility': 10000,
                          'wind': {'speed': 6, 'deg': 240},
                          'rain': {'1h': 0.16},
                          'clouds': {'all': 94},
                          'dt': 1589710794,
                          'sys': {'type': 1,
                           'id': 8903,
                           'country': 'UA',
                           'sunrise': 1589681249,
                           'sunset': 1589737289},
                          'timezone': 10800,
                          'id': 703447,
                          'name': 'Kyiv',
                          'cod': 200}
    :param weather_date: one from:
                        ["/now, "/today", "/tomorrow", "/plus_2_days", "/plus_3_days", "/plus_4_days""]
    :return: finish string for use. For example, '/now' string:
                        "At 2020 May 17, Sunday, 01:19 PM

                        state: light rain
                        temp: 18°-20°
                        clouds: 94%
                        atmo pressure: 1019hPa
                        humidity: 51%
                        wind speed: 6m/s

                        sunrise: 05:07 AM"
                        sunset: 08:41 PM
    """
    if isinstance(weather_data, str):
        return weather_data

    if weather_date == "/now":
        return await parse_weather_api_request(weather_data)
    elif weather_date in ["/today", "/tomorrow", "/plus_2_days", "/plus_3_days", "/plus_4_days"]:
        weather_data = await time_split_weather_message(weather_data, weather_date)
        result_msg = ""
        for one_date in weather_data:
            result_msg += await parse_weather_api_request(one_date)
            result_msg += "\n\n\n"
        return result_msg
    else:
        return "Error, weather message don't create"


__all__ = ["get_weather_data",
           "create_weather_message"]
