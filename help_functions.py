import yaml


def get_data_from_yaml(filename: str) -> dict:
    """
    Get data from yaml
    :param filename: 'filename.yaml'
    :return: {key: values}
    """
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


def admin_check(ADMINS_IDS):
    def wrap(f):
        async def wrapped_f(*args):
            if args[0]['chat']['id'] in ADMINS_IDS:
                value = await f(*args)
                return value

        return wrapped_f

    return wrap
