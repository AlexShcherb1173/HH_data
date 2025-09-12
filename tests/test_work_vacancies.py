# набор тестов для parse_vacancy и parse_vacancies в формате pytest с параметризацией
# с использованием unittest и моков для safe_get_salary
# Что проверяется:#
# parse_vacancy → корректное преобразование полной вакансии.#
# parse_vacancy → обработка вакансии без зарплаты.#
# parse_vacancies → корректная обработка списка вакансий с разными вариантами зарплаты.
# Используется pytest.mark.parametrize для проверки разных вариантов вакансий одной функцией.#
# Мок safe_get_salary используется через patch для полной изоляции тестов.#
# Проверяется правильное преобразование как одной вакансии, так и списка вакансий.
# Тестовый кейс для вакансии без ключа employer, чтобы company_id корректно возвращался как None.#
# Проверка работы функции parse_vacancies на списке вакансий с и без работодателя.

import pytest
from unittest.mock import patch
from src.work_vacancies import parse_vacancy, parse_vacancies

@pytest.mark.parametrize(
    "vacancy_input, mock_return, expected",
    [
        # Обычная вакансия с зарплатой и работодателем
        (
            {
                "id": 123,
                "name": "Python Developer",
                "employer": {"id": 1},
                "salary": {"from": 50000, "to": 70000, "currency": "RUB"},
                "alternate_url": "http://example.com"
            },
            (50000, 70000, "RUB"),
            {
                "vacancy_id": 123,
                "name": "Python Developer",
                "company_id": 1,
                "salary_from": 50000,
                "salary_to": 70000,
                "salary_currency": "RUB",
                "url": "http://example.com"
            }
        ),
        # Вакансия без зарплаты
        (
            {
                "id": 124,
                "name": "Java Developer",
                "employer": {"id": 2},
                "salary": None,
                "alternate_url": "http://example2.com"
            },
            (None, None, None),
            {
                "vacancy_id": 124,
                "name": "Java Developer",
                "company_id": 2,
                "salary_from": None,
                "salary_to": None,
                "salary_currency": None,
                "url": "http://example2.com"
            }
        ),
        # Вакансия без работодателя
        (
            {
                "id": 125,
                "name": "Go Developer",
                "salary": {"from": 60000, "to": 80000, "currency": "USD"},
                "alternate_url": "http://example3.com"
            },
            (60000, 80000, "USD"),
            {
                "vacancy_id": 125,
                "name": "Go Developer",
                "company_id": None,
                "salary_from": 60000,
                "salary_to": 80000,
                "salary_currency": "USD",
                "url": "http://example3.com"
            }
        )
    ]
)
@patch("src.work_vacancies.safe_get_salary")
def test_parse_vacancy(mock_safe_get_salary, vacancy_input, mock_return, expected):
    mock_safe_get_salary.return_value = mock_return
    result = parse_vacancy(vacancy_input)
    assert result == expected
    mock_safe_get_salary.assert_called_once_with(vacancy_input.get("salary"))


@patch("src.work_vacancies.safe_get_salary")
def test_parse_vacancies_list_with_missing_employer(mock_safe_get_salary):
    vacancies = [
        {
            "id": 1,
            "name": "Python Developer",
            "employer": {"id": 1},
            "salary": {"from": 50000, "to": 70000, "currency": "RUB"},
            "alternate_url": "http://example.com"
        },
        {
            "id": 2,
            "name": "Java Developer",
            "salary": None,
            "alternate_url": "http://example2.com"
        }
    ]

    # Возвращаемые значения для двух вакансий
    mock_safe_get_salary.side_effect = [(50000, 70000, "RUB"), (None, None, None)]

    expected = [
        {
            "vacancy_id": 1,
            "name": "Python Developer",
            "company_id": 1,
            "salary_from": 50000,
            "salary_to": 70000,
            "salary_currency": "RUB",
            "url": "http://example.com"
        },
        {
            "vacancy_id": 2,
            "name": "Java Developer",
            "company_id": None,
            "salary_from": None,
            "salary_to": None,
            "salary_currency": None,
            "url": "http://example2.com"
        }
    ]

    result = parse_vacancies(vacancies)
    assert result == expected
    assert mock_safe_get_salary.call_count == 2