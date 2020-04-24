import ast
import statistics
from typing import List, Dict, Union


async def parse_exmo_jsons(raw_data: Dict[str, Union[int, str]], cripto_pair: List[str]) -> Union[Dict[str, str], bool]:
    """
    :param cripto_pair: ['BTC_USD', 'ETH_USD', 'XRP_USD' ... ]
    :param raw_data: {'status': 200,
                      'result': '{'BTC_USD': {'buy_price': '7573.5',
                                              'sell_price': '7574.7319',
                                              'last_trade': '7573.5',
                                              'high': '7616.1926067',
                                              'low': '7150',
                                              'avg': '7412.25958804',
                                              'vol': '496.8726659',
                                              'vol_curr': '3763065.13521417',
                                              'updated': 1587671114},
                                   'BTC_EUR': { ... },
                                   ... }'
                      }

    :return {'BTC_USD': '7580.34561', 'ETH_USD': '189.682', ... }
    """
    # Check correct result request and prepare data using ast.literal_eval method:
    if raw_data and raw_data.get('status') == 200:
        raw_data = ast.literal_eval(raw_data['result'])
    else:
        return False

    # Take specific pairs only:
    data = {pair: pair_data for pair, pair_data in raw_data.items() if pair in cripto_pair}

    # Take average buy/sell price:
    result = {}
    for pair, pair_data in data.items():
        try:
            buy_price = float(pair_data['buy_price'])
            sell_price = float(pair_data['sell_price'])
            average_price = statistics.mean([buy_price, sell_price])
            average_price = round(average_price, 5)
            result[pair] = str(average_price)
        except Exception:
            result[pair] = "haven't result"
    return result


async def create_crypto_currency_message(currency: Union[Dict[str, str], bool]) -> str:
    """
    Create string with crypto currency data

    :param currency: {'BTC_USD': '7580.34561', 'ETH_USD': '189.682', ... }
    :return: 'str'
    """
    if currency:
        currency_str = "Exmo pairs: \n"
        for pair, cost in currency.items():
            currency_str += f"{pair}: {cost}\n"
    else:
        currency_str = "all pairs of currency haven't result"
    return currency_str
