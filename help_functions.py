import yaml
import aiohttp
import asyncio
from typing import List, Dict, Union, Any


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
        async def wrapped_f(*args):
            if args[0]['chat']['id'] in ADMINS_IDS:
                value = await f(*args)
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


def parse_privat_jsons(result: List[Dict[str, Union[int, str]]]):
    """
    [{'status': 200,
      'result': '[{"ccy":"USD","base_ccy":"UAH","buy":"26.85000","sale":"27.25000"}, ...]'},
     {'status': 200,
      'result': '[{"ccy":"USD","base_ccy":"UAH","buy":"26.90000","sale":"27.24796"}, ...]'}]
    """
    return result
