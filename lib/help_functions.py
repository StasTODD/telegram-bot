import os
import signal
from pathlib import Path
from typing import Dict, Union
import asyncio
import aiohttp
import yaml


def get_data_from_yaml(filename: str) -> dict:
    """
    Get data from yaml
    :param filename: 'filename.yaml'
    :return: {key: values}
    """
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def admin_check(ADMINS_IDS):
    """
    Decorator for access admins ID only
    """
    def wrap(f):
        async def wrapped_f(*args, **kwargs):
            if args[0]["chat"]["id"] in ADMINS_IDS:
                value = await f(*args, **kwargs)
                return value
        return wrapped_f
    return wrap


async def get_json_from_web(url: str) -> Dict[str, Union[str, object]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = {"status": resp.status, "result": await resp.text()}
            return result


def create_dir(dir_path: str):
    """
    Create dir
    :param dir_path: 'images/background_template'
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


async def find_pid(attribute: str) -> Union[int, str, bool]:
    """
    Find PID using keyword for searching.
    :param attribute: "rpi_pirsensor_camera_telegram"
    :return: int | str | bool
        int - number of PID
        str - error text message
        bool - (False) PID not found
    """
    # https://queirozf.com/entries/python-3-subprocess-examples#wait-for-command-to-terminate-asynchronously
    command = f"ps ax | grep {attribute} | grep -v grep | awk '{{print $1}}'"
    proc = await asyncio.create_subprocess_shell(command,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    error_msg = stderr.decode()  # ''
    pid = stdout.decode()  # '1234\n'
    result = False
    if pid:
        try:
            result = int(pid)
        except ValueError as e:
            result = e
    if error_msg:
        return error_msg
    if not error_msg and not pid:
        return False
    return result


async def kill_process(pid: int) -> Union[str, bool]:
    """
    Kill PID with SIGKILL option (-9)
    :param pid: int | 3126
    :return: True | 'error text'
    """
    try:
        os.kill(int(pid), signal.SIGKILL)
        return True
    except ProcessLookupError as e:
        return e
    except PermissionError as e:
        return e
    except Exception as e:
        return e


__all__ = ["get_data_from_yaml",
           "admin_check",
           "get_json_from_web",
           "create_dir",
           "find_pid",
           "kill_process"]
