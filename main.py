import logging
import json
import random
import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


def random_integer_partition(volume, number, amountDif, priceMin, priceMax):
    # Приведём все значения к натуральным, найдя десятичное число с наибольшим количеством чисел после запятой
    # После чего домножим все числа на множитель этой десятичной дроби, а в конце поделим на него полученные значения
    multiplier = 10 ** len(str(volume).split('.')[1])
    multiplier = max(multiplier, 10 ** len(str(amountDif).split('.')[1]))
    multiplier = max(multiplier, 10 ** len(str(priceMin).split('.')[1]))
    multiplier = max(multiplier, 10 ** len(str(priceMax).split('.')[1]))
    volume *= multiplier
    amountDif *= multiplier
    priceMin *= multiplier
    priceMax *= multiplier
    if volume < number or number <= 0 or amountDif < 0 or priceMin < 0 or priceMax < 0 or priceMin > priceMax or \
            priceMax * number < volume or priceMin * number > volume:
        return logging.error("Invalid partition parameters")

    result = []
    # Если число одно, то просто возвращаем его
    if number == 1:
        result = [volume / multiplier]
        return result
    # Находим среднее значение и присваиваем его каждому числу, если есть остаток, то распределяем его равномерно
    average_value = volume // number
    addition = volume % number
    for i in range(number):
        if addition > 0:
            result.append(average_value + 1)
            addition -= 1
        else:
            result.append(average_value)
    # Находим минимальное и максимальное значение в пределах которых придадим случайность числам
    max_v = min(priceMax, average_value + amountDif)
    min_v = max(priceMin, average_value - amountDif)
    '''
     Пройдёмся по всем парам чисел, и для каждой пары сделаем так: из первого вычтем случайное число (в границах),
     а ко второму прибавим, каждый раз перед этим проверяя не вышли ли мы за пределы найденных выше границ
     если вышли, то отменяя операцию и не изменяя чисел могут случится ситуации, когда числа не изменятся вовсе, 
     но такой вариант редкий и тоже удовлетворяет условиям как и соответствует элементу случайности.
    '''
    for i in range(1, number):
        # С помощью случайного флага выбираем прибавим ли мы или вычтем
        flag = bool(random.getrandbits(1))
        if flag:
            diff = random.randrange(max_v - result[i] + 1)
            if result[i - 1] - diff >= min_v:
                result[i - 1] -= diff
                result[i] += diff
        else:
            diff = random.randrange(result[i] + 1 - min_v)
            if result[i - 1] + diff <= max_v:
                result[i - 1] += diff
                result[i] -= diff
    # Делим на множитель, который мы умножили в самом начале
    for i in range(number):
        result[i] /= multiplier
    return result


def main_request(api_key, api_secret, json_input):
    # Проверяем можно ли установить соединение с сервером
    try:
        # Тестовая торговля
        client = Client(api_key, api_secret, testnet=True)
        # Реальная торговля
        # client = Client(api_key, api_secret)
        client.ping()
    except Exception:
        return logging.error('Error while connecting to Binance')
    try:
        if json_input['side'] == 'BUY':
            asset_balance = float(client.get_asset_balance(asset='USDT').get('free'))
            if asset_balance < json_input['volume']:
                return logging.error('Not enough money to buy')
            min_notional = json_input['priceMin']
            max_notional = json_input['priceMax']
        elif json_input['side'] == 'SELL':
            info = client.get_symbol_info('BTCUSDT').get('filters')
            # Из информации о валюте найдём минимум и максимум по которой ею можно торговать
            min_notional = float(info[6]['minNotional'])
            max_notional = float(info[6]['maxNotional'])
            min_notional = max(json_input['priceMin'], min_notional)
            max_notional = min(json_input['priceMax'], max_notional)
        else:
            return logging.error('Not sell or buy in request')
    except Exception:
        return logging.error('Incorrect Api-key')
    result = random_integer_partition(
        json_input['volume'], json_input['number'], json_input['amountDif'],
        min_notional, max_notional)
    logging.info(result)
    if result is None:
        return
    for i in range(json_input['number']):
        client.create_test_order(symbol='BTCUSDT', side='BUY', type='MARKET', quoteOrderQty=result[i])


if __name__ == '__main__':
    api_key = os.environ['BINANCE_API_KEY_TEST']
    api_secret = os.environ['BINANCE_API_SECRET_TEST']
    f = open('test1.json')
    json_input = json.load(f)
    main_request(api_key, api_secret, json_input)
    f = open('test2.json')
    json_input = json.load(f)
    main_request(api_key, api_secret, json_input)
    f = open('test3.json')
    json_input = json.load(f)
    main_request(api_key, api_secret, json_input)
    f = open('test5.json')
    json_input = json.load(f)
    main_request(api_key, api_secret, json_input)
    f = open('test6.json')
    json_input = json.load(f)
    main_request(api_key, api_secret, json_input)
    f = open('test7.json')
    json_input = json.load(f)
    main_request(api_key, api_secret, json_input)
