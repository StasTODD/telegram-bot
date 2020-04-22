import yaml
import aiohttp
import logging
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


def action_logging():
    """
    Decorator for logging all actions in to the message_handler and send to logging.info()
    """
    def wrap(f):
        async def wrapped_f(*args, **kwargs):
            # TODO: modify class name check
            message_object = [arg for arg in args if arg.__class__.__name__ == 'Message']
            if message_object:
                message_object = message_object[0]
                first_name = message_object.chat.first_name
                last_name = message_object.chat.last_name
                username = message_object.chat.username
                text = message_object.text
                logging_message = ''
                if first_name:
                    logging_message += f'{first_name} '
                if last_name:
                    logging_message += f'{last_name} '
                if username:
                    logging_message += f'as @{username} '
                logging_message += f'write --> {text}'
                logging.info(logging_message)
            return await f(*args, **kwargs)
        return wrapped_f
    return wrap
