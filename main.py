import json
import os
from datetime import datetime
import requests


API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
CURRENCY_RATES_FILE = "currency_rates.json"
last_checked_times = dict() # словарь для проверки времени последнего запроса


def main():
    """
    Основная функция программы. Получает от пользователя название валюты — USD или EUR,
    получает и выводит на экран текущий курс валюты от API. Записывает данные в JSON-файл.
    """
    while True:
        currency = input("Введите название валюты (USD EUR): ").upper()
        if currency not in ('USD', 'EUR'):
            print('Некорректный ввод')
            continue

        rate = get_currency_rate(currency)
        if is_rate_changed(currency, rate):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f'{timestamp}\nКурс {currency} к рублю {rate}')
            data = {'currency': currency, 'rate': rate, 'timestamp': timestamp}

            save_to_json(data)
        else:
            print('С момента последнего запроса прошло меньше минуты')
        choice = input("Выберите действие: (1 - продолжить, 2 - выйти) ")
        if choice == "1":
            continue
        elif choice == "2":
            break
        else:
            print("Некорректный ввод")
            break


def get_currency_rate(base: str) -> float:
    """Получает курс валюты от API и возвращает его в виде float"""
    url = "https://api.apilayer.com/exchangerates_data/latest"
    response = requests.get(url, headers={'apikey': API_KEY}, params={'base': base})
    rate = response.json()["rates"]["RUB"]
    return rate

    status_code = response.status_code
    result = response.text


def save_to_json(data: dict) -> None:
    """Сохраняет данные в JSON-файл"""

    with open(CURRENCY_RATES_FILE, "a") as f:
        if os.stat(CURRENCY_RATES_FILE).st_size == 0:
            json.dump([data], f)
        else:
            with open(CURRENCY_RATES_FILE) as json_file:
                data_list = json.load(json_file)
            data_list.append(data)
            with open(CURRENCY_RATES_FILE, "w") as json_file:
                json.dump(data_list, json_file)



def is_rate_changed(currency: str, new_rate: float) -> bool:
    """
    Проверяет, отличается ли текущий курс валюты от курса, который уже хранится в файле,
    и проверяет, прошла ли минута с последней проверки.
    Возвращает True, если курс отличается и прошло более минуты с последней проверки, и False в противном случае.
    """
    global last_checked_times
    current_time = datetime.now()

    # Проверяем, была ли уже проверка для данной валюты
    if currency in last_checked_times:
        # Получаем время последней проверки
        last_checked_time = last_checked_times[currency]
        # Проверяем, прошла ли минута с последней проверки
        time_difference = current_time - last_checked_time
        if time_difference.total_seconds() < 60:
            return False  # Пропускаем проверку, если прошло менее минуты
    else:
        # Если это первая проверка для данной валюты, устанавливаем время текущее время
        last_checked_times[currency] = current_time

    try:
        with open(CURRENCY_RATES_FILE) as json_file:
            data_list = json.load(json_file)
            for data in data_list:
                if data['currency'] == currency:
                    # Получаем курс из последней записи в файле
                    old_rate = data['rate']
                    # Проверяем, отличается ли новый курс от старого
                    if new_rate != old_rate:
                        # Обновляем время последней проверки для данной валюты
                        last_checked_times[currency] = current_time
                        return True
                    else:
                        return False
            # Если в файле нет записей для данной валюты, считаем, что курс отличается
            return True
    except FileNotFoundError:
        # Если файл не найден, считаем, что курс отличается
        return True


if __name__ == '__main__':
    main()
