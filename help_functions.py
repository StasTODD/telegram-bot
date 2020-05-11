import yaml
import aiohttp
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
        async def wrapped_f(*args, **kwargs):
            if args[0]['chat']['id'] in ADMINS_IDS:
                value = await f(*args, **kwargs)
                return value
        return wrapped_f
    return wrap


async def get_json_from_web(url: str) -> Dict[str, Union[str, object]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = {'status': resp.status, 'result': await resp.text()}
            return result

__all__ = ['get_data_from_yaml',
           'admin_check',
           'get_json_from_web']
