import ast
import statistics
from typing import List, Dict, Union
from PIL import Image, ImageDraw, ImageFont
from .help_functions import create_dir


# EXMO exchange API (JSON format)
url_exmo = "https://api.exmo.com/v1.1/ticker"
cripto_pair = ["BTC_USD", "ETH_USD", "XRP_USD", "EOS_USD",
               "ETC_USD", "LTC_USD", "NEO_USD", "SMART_USD",
               "XEM_USD", "XLM_USD", "XMR_USD"]


async def parse_exmo_jsons(raw_data: Dict[str, Union[int, str]], cripto_pair: List[str]) -> Union[Dict[str, str], bool]:
    """
    :param cripto_pair: ['BTC_USD', 'ETH_USD', 'XRP_USD' ... ]
    :param raw_data: {'status': 200,
                      'result': '{'BTC_USD': {'buy_price': '7573.5',
                                              'sell_price': '7574.7319',
                                              'last_trade': '7573.5',
                                              'high': '7616.1926067',
                                              'low': '7150',
                                              'avg': '7412.25958804',
                                              'vol': '496.8726659',
                                              'vol_curr': '3763065.13521417',
                                              'updated': 1587671114},
                                   'BTC_EUR': { ... },
                                   ... }'
                      }

    :return {'BTC_USD': '7580.34561', 'ETH_USD': '189.682', ... }
    """
    # Check correct result request and prepare data using ast.literal_eval method:
    if raw_data and raw_data.get("status") == 200:
        raw_data = ast.literal_eval(raw_data["result"])
    else:
        return False

    # Take specific pairs only:
    data = {pair: pair_data for pair, pair_data in raw_data.items() if pair in cripto_pair}

    # Take average buy/sell price:
    result = {}
    for pair, pair_data in data.items():
        try:
            buy_price = float(pair_data["buy_price"])
            sell_price = float(pair_data["sell_price"])
            average_price = statistics.mean([buy_price, sell_price])
            average_price = round(average_price, 5)
            result[pair] = str(average_price)
        except Exception:
            result[pair] = "haven't result"
    return result


async def create_cryptocurrency_message(currency: Union[Dict[str, str], bool], text_for_image: bool = False) -> str:
    """
    Create string with crypto currency data

    :param text_for_image: Display output information in images (images - True, text - False)
    :param currency: {'BTC_USD': '7580.34561', 'ETH_USD': '189.682', ... }
    :return: 'str'
    """
    if not currency and not isinstance(currency, dict):
        return "all pairs of currency haven't result"

    if not text_for_image:
        currency_str = "Exmo pairs: \n"
        for pair, cost in currency.items():
            currency_str += f"{pair}:   {cost}\n"
        return currency_str
    else:
        currency_str = "Exmo pairs: \n\n\n"
        for pair, cost in currency.items():
            currency_str += f"{pair}:   {cost}\n\n"
        return currency_str


async def create_cryptocurrency_image(displayed_text: str) -> str:
    """
    Create images with text and return path to images

    :param displayed_text: str
    :return: "images/out/crypto.png"
    """
    template_directory = "images/background_template"
    result_directory = "images/out"
    image_name = "crypto.png"
    image_template_path = f"{template_directory}/{image_name}"
    image_result_path = f"{result_directory}/{image_name}"
    image_template = Image.open(image_template_path)
    draw = ImageDraw.Draw(image_template)

    font_size = 50
    font = ImageFont.truetype("images/fonts/Spartan/static/Spartan-SemiBold.ttf", size=font_size)

    # Start position on images:
    (x, y) = (140, 90)

    text_color = "rgb(255, 255, 255)"

    draw.text((x, y), displayed_text, fill=text_color, font=font)
    try:
        image_template.save(image_result_path)
    except FileNotFoundError:
        create_dir(result_directory)
        image_template.save(image_result_path)

    return image_result_path

__all__ = ["url_exmo",
           "cripto_pair",
           "parse_exmo_jsons",
           "create_cryptocurrency_message",
           "create_cryptocurrency_image"]
