import platform
import asyncio
from .help_functions import get_json_from_web


async def get_public_ip() -> str:
    """
    It's not universal function for work with sites who response me with data of my public IP address
    :return: 'ip address'
    """
    url_ip_0 = "https://api.ipify.org/"
    url_ip_1 = "https://ident.me/"

    requests_list = [await get_json_from_web(url) for url in [url_ip_0, url_ip_1]]

    results_data_list = []
    for one_request in requests_list:
        if one_request.get("status") == 200:
            request_result = one_request.get("result")
            results_data_list.append(request_result)

    if len(set(results_data_list)) == 1:
        return str(results_data_list[0])
    else:
        return f"something wrong: {', '.join(results_data_list)}"


async def get_software_info() -> str:
    """
    Get and return python and OS information (version)
    :return: 'os: info
              python: info'
    """
    python_version = platform.python_version()
    os_version = platform.system()
    os_release = platform.release()
    os_data = f"{os_version} {os_release}"
    software_info = f"os: {os_data}\n" \
                    f"python: {python_version}"

    return software_info


async def get_hardware_info() -> str:
    """
    Get and return cpu architecture information
    :return: 'cpu: armv7l'
    """
    hardware_info = platform.uname()
    machine = hardware_info.machine
    if len(machine):
        return f"cpu: {str(machine)}"
    else:
        return ""


async def get_cpu_temperature():
    """
    Async function for getting CPU temperature.
    :return: str() | Text with error 'ERROR: CPU temperature can not be obtained' or temperature value '41.8°C'
    """
    command = f"cat /sys/class/thermal/thermal_zone*/temp"
    proc = await asyncio.create_subprocess_shell(command,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    error_msg = stderr.decode()  # ''
    temperature = stdout.decode()  # '41868\n'
    result = str()
    if temperature:
        try:
            result = str(int(temperature)/1000)[:4]  # '41.8'
        except ValueError as e:
            return "ERROR: CPU temperature can not be decoded"
    if error_msg:
        return "ERROR: CPU temperature was obtained with error"
    if not error_msg and not temperature:
        return "ERROR: CPU temperature can not be obtained"
    return f"{result}°C"


async def all_messages_text() -> str:
    """
    Collecting different data about Telegram-bot platform/environment
    :return: 'information text'
    """
    public_ip = await get_public_ip()
    software_info = await get_software_info()
    hardware_info = await get_hardware_info()
    cpu_temperature = await get_cpu_temperature()

    message_text = "<code>"
    if public_ip:
        message_text += f"it works from IP: {public_ip}\n"
    if software_info:
        message_text += f"{software_info}\n"
    if hardware_info:
        message_text += f"{hardware_info}\n"
    if cpu_temperature:
        message_text += f"CPU temperature: {cpu_temperature}\n"
    message_text += "</code>"
    if not message_text:
        message_text = "Haven't information"

    return message_text

__all__ = ["all_messages_text"]
