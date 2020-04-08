def get_api_token(filename: str):
    """
    Get Telegram API TOKEN from file
    :param filename: 'filename.txt'
    :return: 'token symbols'
    """
    with open(filename, 'r') as f:
        return f.read().rstrip()
