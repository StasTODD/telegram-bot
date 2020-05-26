from help_functions import get_json_from_web
import ast


async def get_public_ip() -> str:
    """
    It's not universal function for work with sites who response me with data of my public IP address
    :return: 'ip address'
    """
    # TODO: Using try/except its not good idea, need something better:
    url_ip_0 = "https://api.ipify.org?format=json"
    url_ip_1 = "https://ident.me/"

    requests_list = [await get_json_from_web(url) for url in [url_ip_0, url_ip_1]]

    results_data_list = []
    for one_request in requests_list:
        if one_request.get("status") == 200:
            request_result = one_request.get("result")
            try:
                request_result = ast.literal_eval(request_result)
                request_result = request_result.get("ip")
                results_data_list.append(request_result)
            except SyntaxError:
                results_data_list.append(request_result)

    if len(set(results_data_list)) == 1:
        return str(results_data_list[0])
    else:
        return f"something wrong: {', '.join(results_data_list)}"


async def get_operation_system_info():
    operation_system_info = "operation_system_info"
    # TODO: need write logic
    return operation_system_info


async def get_hardware_info():
    hardware_info = "hardware_info"
    # TODO: need write logic
    return hardware_info


async def all_messages_text() -> str:
    """
    Collecting different data about Telegram-bot platform/environment
    :return: 'information text'
    """
    public_ip = await get_public_ip()
    operation_system_info = await get_operation_system_info()
    hardware_info = await get_hardware_info()

    message_text = ""
    if public_ip:
        message_text += f"Work from IP: {public_ip}\n"
    if operation_system_info:
        message_text += f"{operation_system_info}\n"
    if hardware_info:
        message_text += f"{hardware_info}\n"
    if not message_text:
        message_text = "Haven't information"

    return message_text

__all__ = ["all_messages_text"]
