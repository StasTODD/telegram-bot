import asyncio
import ast
from typing import List, Dict, Union, Any
from help_functions import get_json_from_web


async def get_jsons_privat(url_list: List[str]) -> list:
    coroutines = map(get_json_from_web, url_list)
    return await asyncio.gather(*coroutines)


async def parse_privat_jsons(raw_data: List[Dict[str, Union[int, str]]]) -> List[Dict[str, str]]:
    """
    :param raw_data: [{'status': 200,
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
    :return: 'str'
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
