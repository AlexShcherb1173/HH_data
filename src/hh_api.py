# hh.ru API позволяет запросы по работодателю и /vacancies.
# использует requests, реализует класс для получения компаний и вакансий

import os
from typing import Dict, List

import certifi
import requests
from dotenv import load_dotenv

from src.services import safe_get_salary

load_dotenv(encoding="utf-8")


class HHApi:
    """Класс для работы с публичным API hh.ru. Позволяет получать компании и вакансии.
    Настраивает параметры поиска (регион, размер страницы).
    Задаёт таймауты для стабильности (чтобы запросы не "висели" вечно).
    Создаёт HTTP-сессию с правильным SSL и заголовками."""

    BASE_URL = os.getenv("HH_API_URL", "https://api.hh.ru")  # Берём переменную окружения HH_API_URL из .env
    # Если переменной нет → используем дефолтный адрес API https://api.hh.ru.

    def __init__(self, area: int = 113, per_page: int = 50, connect_timeout: int = 5, read_timeout: int = 10):
        """
        :param area: ID региона (Россия = 113)
        :param per_page: количество вакансий за один запрос (максимум 100)
        :param connect_timeout: таймаут подключения
        :param read_timeout: таймаут ответа
        """
        self.area = area  # Сохраняем параметры
        self.per_page = per_page  # Сохраняем параметры
        self.timeout = (connect_timeout, read_timeout)  # self.timeout хранится как кортеж, то, что передаётся
        # в requests.get(..., timeout=self.timeout).
        self.session = requests.Session()  # Создаём HTTP-сессию
        # Сессия позволяет переиспользовать одно соединение.
        self.session.verify = certifi.where()  # Говорим requests, где лежат корневые сертификаты
        # (через библиотеку certifi). Это гарантирует, что SSL-подключение
        # к api.hh.ru будет верифицировано, и исключает ошибки вида ssl.SSLError.
        self.session.headers.update(
            {  # Устанавливаем кастомный заголовок User-Agent.
                "User-Agent": "HH-Data-Collector/1.0"  # Многие API (включая hh.ru) требуют, чтобы у клиента был
                # свой User-Agent, а не дефолтный
            }
        )

    def get_companies(self, text: str = "IT") -> List[Dict]:
        """Получить список работодателей (компаний) с hh.ru по ключевому слову (по умолчанию "IT")."""
        companies: List[Dict] = []  # Инициализируется пустой список companies.
        page = 0  # Переменная page = 0 — будем ходить по страницам API.
        while len(companies) < 15:
            url = f"{self.BASE_URL}/employers"  # Формируется URL https://api.hh.ru/employers.
            params: dict[str, str | int] = {
                "text": text,
                "area": self.area,
                "page": page,
                "per_page": 50,
            }  # Запрашиваются данные с
            # параметрами:
            # text → ключевое слово поиска (например, "IT")
            # area → регион (по умолчанию Россия = 113)
            # page → номер страницы
            # per_page = 50 → по 50 компаний за раз.
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении компаний: {e}")
                break
            data = response.json()  # Если запрос успешен: Берется JSON-ответ data.
            for item in data.get("items", []):  # Перебираются все компании из data["items"].
                if item.get("open_vacancies", 0) > 0:  # Если у компании есть открытые вакансии (open_vacancies > 0) →

                    companies.append({"id": int(item["id"]), "name": item["name"]})  # добавляем словарь
                    # {id, name} в список.
                    if len(companies) >= 15:  # Как только набирается 15 компаний, выходим из цикла.
                        break
            if page >= data.get("pages", 1) - 1:
                break
            page += 1
        # Возвращается список максимум из 15 компаний.
        return companies[:15]

    def get_vacancies_for_company(self, employer_id: int) -> List[Dict]:
        """Получить список вакансий для конкретной компании по её employer_id с сайта hh.ru."""
        vacancies: List[Dict] = []  # Создаётся пустой список vacancies.
        page = 0  # Устанавливается page = 0 для постраничной загрузки вакансий.
        while True:  # В бесконечном цикле (while True):
            url = f"{self.BASE_URL}/vacancies"  # Формируется запрос к API https://api.hh.ru/vacancies с параметрами:
            params = {
                "employer_id": employer_id,  # employer_id → ID работодателя
                "area": self.area,  # area → регион (по умолчанию Россия = 113)
                "page": page,  # page → номер страницы
                "per_page": self.per_page,  # per_page → сколько вакансий брать за один запрос
            }
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)  # Отправляется GET-запрос
                # с requests.Session
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении вакансий для компании {employer_id}: {e}")
                break
            data = response.json()  # Если запрос успешен → берётся JSON-ответ.
            for v in data.get("items", []):  # Для каждой вакансии в data["items"]:
                salary_from, salary_to, currency = safe_get_salary(v.get("salary"))  # Извлекаются зарплата
                # (from, to, currency) через метод safe_get_salary.

                # Формируется словарь с ключевыми данными и добавляется в список vacancies.:
                vacancies.append(
                    {
                        "vacancy_id": int(v["id"]),  # "vacancy_id": int(v["id"]),
                        "company_id": employer_id,  # "company_id": employer_id,
                        "name": v["name"],  # "name": v["name"],
                        "salary_from": salary_from,  # "salary_from": salary_from,
                        "salary_to": salary_to,  # "salary_to": salary_to,
                        "salary_currency": currency,  # "salary_currency": currency,
                        "url": v["alternate_url"],  # "url": v["alternate_url"]
                    }
                )
            if page >= data.get("pages", 1) - 1:  # Если достигнута последняя страница цикл прерывается.
                break
            page += 1  # Иначе page увеличивается на 1 и цикл продолжается.
        return vacancies
