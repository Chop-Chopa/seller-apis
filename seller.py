import io
import logging.config
import os
import re
import zipfile
from environs import Env

import pandas as pd
import requests

logger = logging.getLogger(__file__)


def get_product_list(last_id, client_id, seller_token):
    """
    Получает список товаров магазина Ozon.

    Эта функция делает запрос к API Ozon и получает информацию о товарах,
    начиная с указанного товара (по ID), и возвращает данные о товарах.

    Аргументы:
        last_id (str): ID последнего товара, с которого нужно начать загрузку.
        client_id (str): ID клиента для аутентификации в API Ozon.
        seller_token (str): Токен продавца для доступа к API Ozon.

    Возвращает:
        list: Список товаров магазина Ozon в формате JSON. Каждый товар содержит
              информацию, такую как ID, название, описание и другие параметры.

    Пример:
        >>> get_product_list('12345', 'client_id_example', 'token_example')
        [{'offer_id': '12345', 'name': 'Товар 1'}, {'offer_id': '12346', 'name': 'Товар 2'}]

    Некорректное использование:
        >>> get_product_list('', 'client_id_example', 'token_example')
        []  # Если нет товаров с таким last_id, возвращается пустой список.
    """
    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {
        "filter": {
            "visibility": "ALL",
        },
        "last_id": last_id,
        "limit": 1000,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def get_offer_ids(client_id, seller_token):
    """
    Получает артикулы товаров магазина Ozon.

    Функция делает несколько запросов к API Ozon для получения всех артикулов товаров магазина.

    Аргументы:
        client_id (str): ID клиента для аутентификации в API Ozon.
        seller_token (str): Токен продавца для доступа к API Ozon.

    Возвращает:
        list: Список артикулов товаров магазина Ozon.

    Пример:
        >>> get_offer_ids('client_id_example', 'token_example')
        ['offer_id_1', 'offer_id_2']

    Некорректное использование:
        >>> get_offer_ids('invalid_client', 'invalid_token')
        []  # Если не удаётся получить данные, вернётся пустой список.
    """
    last_id = ""
    product_list = []
    while True:
        some_prod = get_product_list(last_id, client_id, seller_token)
        product_list.extend(some_prod.get("items"))
        total = some_prod.get("total")
        last_id = some_prod.get("last_id")
        if total == len(product_list):
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer_id"))
    return offer_ids


def update_price(prices: list, client_id, seller_token):
    """
    Обновляет цены товаров на Ozon.

    Функция отправляет запрос в API Ozon для обновления цен товаров по списку.

    Аргументы:
        prices (list): Список словарей с ценами товаров, где каждый словарь содержит 
                       информацию о товаре и новой цене.
        client_id (str): ID клиента для аутентификации в API Ozon.
        seller_token (str): Токен продавца для доступа к API Ozon.

    Возвращает:
        dict: Ответ от API Ozon, содержащий результат обновления цен.

    Пример:
        >>> update_price([{'offer_id': '12345', 'price': '5990'}], 'client_id_example', 'token_example')
        {'result': 'success'}

    Некорректное использование:
        >>> update_price([], 'client_id_example', 'token_example')
        {'error': 'No prices to update'}
    """
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"prices": prices}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_stocks(stocks: list, client_id, seller_token):
    """
    Обновляет остатки товаров на Ozon.

    Функция отправляет запрос в API Ozon для обновления остатков товаров по списку.

    Аргументы:
        stocks (list): Список словарей с остатками товаров, где каждый словарь содержит
                       информацию о товаре и новом остатке.
        client_id (str): ID клиента для аутентификации в API Ozon.
        seller_token (str): Токен продавца для доступа к API Ozon.

    Возвращает:
        dict: Ответ от API Ozon, содержащий результат обновления остатков.

    Пример:
        >>> update_stocks([{'offer_id': '12345', 'stock': 100}], 'client_id_example', 'token_example')
        {'result': 'success'}

    Некорректное использование:
        >>> update_stocks([], 'client_id_example', 'token_example')
        {'error': 'No stocks to update'}
    """
    url = "https://api-seller.ozon.ru/v1/product/import/stocks"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"stocks": stocks}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def download_stock():
    """
    Скачивает файл с остатками товаров с сайта Casio.

    Эта функция загружает файл с остатками, распаковывает его и извлекает данные
    из Excel файла для дальнейшего использования.

    Возвращает:
        list: Список остатков товаров в формате словарей, где каждый словарь содержит
              информацию о товаре и его остатке.

    Пример:
        >>> download_stock()
        [{'Код': '12345', 'Количество': '5'}, {'Код': '12346', 'Количество': '>10'}]

    Некорректное использование:
        >>> download_stock()
        []  # Если файл повреждён или данные не загружаются, возвращается пустой список.
    """
    # Скачать остатки с сайта
    casio_url = "https://timeworld.ru/upload/files/ostatki.zip"
    session = requests.Session()
    response = session.get(casio_url)
    response.raise_for_status()
    with response, zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(".")
    # Создаем список остатков часов:
    excel_file = "ostatki.xls"
    watch_remnants = pd.read_excel(
        io=excel_file,
        na_values=None,
        keep_default_na=False,
        header=17,
    ).to_dict(orient="records")
    os.remove("./ostatki.xls")  # Удалить файл
    return watch_remnants


def create_stocks(watch_remnants, offer_ids):
    """
    Создаёт список остатков для товаров на Ozon.

    Эта функция фильтрует остатки, чтобы оставить только те товары, которые
    уже загружены на Ozon, и добавляет недостающие товары с нулевым остатком.

    Аргументы:
        watch_remnants (list): Список словарей с остатками товаров.
        offer_ids (list): Список артикулов товаров на Ozon.

    Возвращает:
        list: Список словарей с остатками товаров для загрузки на Ozon.

    Пример:
        >>> create_stocks([{'Код': '12345', 'Количество': '5'}], ['12345'])
        [{'offer_id': '12345', 'stock': 5}]

    Некорректное использование:
        >>> create_stocks([], [])
        []
    """
    stocks = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append({"offer_id": str(watch.get("Код")), "stock": stock})
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append({"offer_id": offer_id, "stock": 0})
    return stocks


def create_prices(watch_remnants, offer_ids):
    """
    Создаёт список цен для товаров на Ozon.

    Эта функция формирует список цен для товаров, которые есть на Ozon, 
    используя данные из списка остатков.

    Аргументы:
        watch_remnants (list): Список словарей с остатками товаров.
        offer_ids (list): Список артикулов товаров на Ozon.

    Возвращает:
        list: Список словарей с ценами товаров для загрузки на Ozon.

    Пример:
        >>> create_prices([{'Код': '12345', 'Цена': "5'990.00 руб."}], ['12345'])
        [{'offer_id': '12345', 'price': '5990'}]

    Некорректное использование:
        >>> create_prices([], [])
        []
    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": str(watch.get("Код")),
                "old_price": "0",
                "price": price_conversion(watch.get("Цена")),
            }
            prices.append(price)
    return prices


def price_conversion(price: str) -> str:
    """
    Преобразует цену из строки формата "5'990.00 руб." в числовой формат без разделителей.

    Это полезно, когда нужно удалить все символы, кроме цифр, из строки цены, 
    чтобы преобразовать её в стандартный числовой вид, например, для дальнейших расчётов.

    Аргументы:
        price (str): Строка, содержащая цену в формате с разделителями (например, "5'990.00 руб.").

    Возвращает:
        str: Цена в виде строки без разделителей (например, "5990").

    Пример:
        >>> price_conversion("5'990.00 руб.")
        '5990'

    Некорректное использование:
        >>> price_conversion("1000 руб.")
        '1000'
    """
    return re.sub("[^0-9]", "", price.split(".")[0])


def divide(lst: list, n: int):
    """
    Разделяет список на части.

    Эта функция разделяет исходный список на несколько частей, каждая из которых
    имеет не более n элементов.

    Аргументы:
        lst (list): Список, который нужно разделить.
        n (int): Максимальное количество элементов в каждой части.

    Возвращает:
        generator: Генератор, который возвращает части исходного списка,
                   каждая из которых является списком длиной не более n.

    Пример:
        >>> list(divide([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]

    Некорректное использование:
        >>> list(divide([], 2))
        []  # Пустой список остаётся пустым, не вызывает ошибок.
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def upload_prices(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_price in list(divide(prices, 1000)):
        update_price(some_price, client_id, seller_token)
    return prices


async def upload_stocks(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    stocks = create_stocks(watch_remnants, offer_ids)
    for some_stock in list(divide(stocks, 100)):
        update_stocks(some_stock, client_id, seller_token)
    not_empty = list(filter(lambda stock: (stock.get("stock") != 0), stocks))
    return not_empty, stocks


def main():
    env = Env()
    seller_token = env.str("SELLER_TOKEN")
    client_id = env.str("CLIENT_ID")
    try:
        offer_ids = get_offer_ids(client_id, seller_token)
        watch_remnants = download_stock()
        # Обновить остатки
        stocks = create_stocks(watch_remnants, offer_ids)
        for some_stock in list(divide(stocks, 100)):
            update_stocks(some_stock, client_id, seller_token)
        # Поменять цены
        prices = create_prices(watch_remnants, offer_ids)
        for some_price in list(divide(prices, 900)):
            update_price(some_price, client_id, seller_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
