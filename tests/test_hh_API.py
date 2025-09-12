# напишем тесты с использованием pytest и unittest.mock для класса HHApi,
# чтобы не делать реальных запросов к API hh.ru. Мы замокируем requests.Session.get и проверим корректность
# работы методов get_companies и get_vacancies_for_company.
# В этом наборе тестов:#
# mock_get подменяет requests.Session.get → нет реальных HTTP-запросов.#
# mock_safe_salary подменяет функцию safe_get_salary, чтобы тест не зависел от её реализации.#
# Проверяется: фильтрация компаний без вакансий, правильность парсинга вакансий и зарплат, корректная работа при пустом ответе.

import pytest
from unittest.mock import patch, MagicMock
from src.hh_api import HHApi
from src.services import safe_get_salary

# --- Тест get_companies --- #
@patch("src.hh_api.requests.Session.get")
def test_get_companies(mock_get):
    # Подменяем ответ API
    mock_response = MagicMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json.return_value = {
        "items": [
            {"id": "1", "name": "Company1", "open_vacancies": 5},
            {"id": "2", "name": "Company2", "open_vacancies": 0},  # Должна быть пропущена
            {"id": "3", "name": "Company3", "open_vacancies": 10},
        ],
        "pages": 1
    }
    mock_get.return_value = mock_response

    api = HHApi()
    companies = api.get_companies("IT")

    assert len(companies) == 2  # Пропускаем компанию без вакансий
    assert companies[0]["id"] == 1
    assert companies[1]["id"] == 3
    assert companies[0]["name"] == "Company1"

# --- Тест get_vacancies_for_company --- #
@patch("src.hh_api.safe_get_salary", return_value=(100000, 150000, "RUR"))
@patch("src.hh_api.requests.Session.get")
def test_get_vacancies_for_company(mock_get, mock_safe_salary):
    mock_response = MagicMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json.return_value = {
        "items": [
            {"id": "101", "name": "Dev1", "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
             "alternate_url": "http://hh.ru/vacancy/101"}
        ],
        "pages": 1
    }
    mock_get.return_value = mock_response

    api = HHApi()
    vacancies = api.get_vacancies_for_company(1)

    assert len(vacancies) == 1
    v = vacancies[0]
    assert v["vacancy_id"] == 101
    assert v["company_id"] == 1
    assert v["salary_from"] == 100000
    assert v["salary_to"] == 150000
    assert v["salary_currency"] == "RUR"
    assert v["url"] == "http://hh.ru/vacancy/101"
    mock_safe_salary.assert_called_once()

# --- Тест обработки пустого ответа --- #
@patch("src.hh_api.requests.Session.get")
def test_get_companies_empty(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json.return_value = {"items": [], "pages": 1}
    mock_get.return_value = mock_response

    api = HHApi()
    companies = api.get_companies("NonExisting")
    assert companies == []

@patch("src.hh_api.requests.Session.get")
def test_get_vacancies_for_company_empty(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json.return_value = {"items": [], "pages": 1}
    mock_get.return_value = mock_response

    api = HHApi()
    vacancies = api.get_vacancies_for_company(999)
    assert vacancies == []