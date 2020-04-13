import yaml
import aiohttp
import asyncio
from typing import List, Dict, Union, Any
import ast


def get_data_from_yaml(filename: str) -> dict:
    """
    Get data from yaml
    :param filename: 'filename.yaml'
    :return: {key: values}
    """
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


def admin_check(ADMINS_IDS):
    """
    Decorator for access admins ID only
    """
    def wrap(f):
        async def wrapped_f(*args, **kwargs):
            if args[0]['chat']['id'] in ADMINS_IDS:
                value = await f(*args, **kwargs)
                return value
        return wrapped_f
    return wrap


async def get_json_from_web(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = {'status': resp.status, 'result': await resp.text()}
            return result


async def get_jsons_privat(url_list: List[str]):
    coroutines = map(get_json_from_web, url_list)
    return await asyncio.gather(*coroutines)


async def parse_privat_jsons(raw_data: List[Dict[str, Union[int, str]]]):
    """
    [{'status': 200,
      'result': '[{"ccy":"USD","base_ccy":"UAH","buy":"26.85000","sale":"27.25000"}, ...]'},
     {'status': 200,
      'result': '[{"ccy":"USD","base_ccy":"UAH","buy":"26.90000","sale":"27.24796"}, ...]'}]

    :return [{'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.85000', 'sale': '27.25000'},
             {'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.90000', 'sale': '27.24796'}]
    """
    # Check correct result request and rebuild list with data:
    raw_data = [row['result'] for row in raw_data if row.get('result') and row.get('status') == 200]
    # Transform str -> List[Dict[str, str]] using ast.literal_eval method:
    raw_data = [ast.literal_eval(row) for row in raw_data]
    # Taking USD only:
    raw_data = [[currency for currency in row if currency.get('ccy') == 'USD'][0] for row in raw_data]
    return raw_data


async def create_currency_message(currency: List[Dict[str, str]]) -> str:
    """
    Create string with currency data

    Func arg position 0 - for retail
    Func arg position 1 - for business

    :param currency: [{'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.85000', 'sale': '27.25000'},
                      {'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.90000', 'sale': '27.24796'}]
    :return:
    """
    if not isinstance(currency, list):
        return "Haven't data..."

    retail_buy = currency[0]['buy']
    retail_sell = currency[0]['sale']
    business_buy = currency[1]['buy']
    business_sell = currency[1]['sale']
    currency_str = f'Retail:\n' \
                   f'BUY USD: {retail_buy} UAH\n' \
                   f'SELL USD: {retail_sell} UAH\n' \
                   f'\n' \
                   f'Business:\n' \
                   f'BUY USD: {business_buy} UAH\n' \
                   f'SELL USD: {business_sell} UAH\n'
    return currency_str
