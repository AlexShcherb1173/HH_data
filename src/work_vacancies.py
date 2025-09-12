from typing import Dict, List

from src.services import safe_get_salary


def parse_vacancy(vacancy: Dict) -> Dict:
    """Преобразует вакансию из API в словарь для вставки в БД.
    :param vacancy: словарь из API HH
    :return: словарь с ключами: name, company_id, salary_from, salary_to, salary_currency, url"""
    # Превращает «сырые» данные из API в аккуратный словарь, который легко вставлять в таблицу vacancies базы данных.
    # Функция принимает один аргумент vacancy — это словарь, полученный от API HH.ru.
    # Возвращает новый словарь, пригодный для вставки в базу данных.    #
    # В нём будут только нужные поля, с понятными ключами.

    # Извлекаем данные о зарплате с помощью функции safe_get_salary.    #
    # Функция возвращает кортеж (salary_from, salary_to, currency) безопасно, даже если данные отсутствуют.
    salary_from, salary_to, salary_currency = safe_get_salary(vacancy.get("salary"))

    # Формируем словарь с ключами, которые совпадают с колонками в таблице БД:
    return {
        "vacancy_id": int(vacancy["id"]),  # "vacancy_id" — id вакансии.
        "name": vacancy.get("name"),  # "name" — название вакансии.
        "company_id": vacancy.get("employer", {}).get("id"),  # "company_id" — ID работодателя (вложено в employer).
        "salary_from": salary_from,  # "salary_from" — минимальная и
        "salary_to": salary_to,  # "salary_to" — максимальная зарплата.
        "salary_currency": salary_currency,  # "salary_currency" — валюта.
        "url": vacancy.get("alternate_url"),  # "url" — ссылка на вакансию.
    }


def parse_vacancies(vacancies: List[Dict]) -> List[Dict]:
    """Применяет parse_vacancy ко всем вакансиям в списке."""
    # Обёртка для пакетной обработки списка вакансий.
    # Автоматически проходит по всем вакансиям из API и возвращает их в стандартизированном виде,
    # чтобы можно было сразу вызывать DBManager.insert_vacancies(parsed_list).
    # vacancies: List[Dict] — входной аргумент: список словарей, каждый из которых представляет вакансию,
    # как её возвращает API HH.ru.
    # Возвращает List[Dict] — список уже «очищенных» словарей, готовых для вставки в базу данных.

    # Используется list comprehension: для каждой вакансии v из списка vacancies вызывается функция parse_vacancy(v).
    # Результатом работы будет новый список словарей, где каждая вакансия уже подготовлена для базы данных.
    return [parse_vacancy(v) for v in vacancies]
