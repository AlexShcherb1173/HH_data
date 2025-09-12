# Вот полный набор тестов с функциями safe_get_salary, format_salary и format_vacancy с использованием unittest:
# В этом наборе проверены все ключевые случаи:#
# safe_get_salary → None, пустой словарь, частичные данные, все данные.#
# format_salary → обе границы, только from, только to, отсутствующие зарплаты.#
# format_vacancy → полный набор данных, только from, только to, отсутствующие зарплаты.

import unittest
from src.services import safe_get_salary, format_salary, format_vacancy

class TestSalaryUtils(unittest.TestCase):

    # ------------------- Тесты для safe_get_salary -------------------
    def test_safe_get_salary_none(self):
        self.assertEqual(safe_get_salary(None), (None, None, None))

    def test_safe_get_salary_empty_dict(self):
        self.assertEqual(safe_get_salary({}), (None, None, None))

    def test_safe_get_salary_partial(self):
        self.assertEqual(safe_get_salary({"from": 50000}), (50000, None, None))
        self.assertEqual(safe_get_salary({"to": 70000}), (None, 70000, None))
        self.assertEqual(safe_get_salary({"currency": "RUB"}), (None, None, "RUB"))

    def test_safe_get_salary_full(self):
        salary = {"from": 50000, "to": 70000, "currency": "RUB"}
        self.assertEqual(safe_get_salary(salary), (50000, 70000, "RUB"))

    # ------------------- Тесты для format_salary -------------------
    def test_format_salary_none(self):
        self.assertEqual(format_salary(None, None, None), "не указана")

    def test_format_salary_from_only(self):
        self.assertEqual(format_salary(50000, None, "RUB"), "от 50000 RUB")

    def test_format_salary_to_only(self):
        self.assertEqual(format_salary(None, 70000, "RUB"), "до 70000 RUB")

    def test_format_salary_from_to(self):
        self.assertEqual(format_salary(50000, 70000, "RUB"), "от 50000 до 70000 RUB")

    # ------------------- Тесты для format_vacancy -------------------
    def test_format_vacancy_full(self):
        vacancy = {
            "name": "Python Developer",
            "company": "TechCorp",
            "salary_from": 50000,
            "salary_to": 70000,
            "salary_currency": "RUB",
            "url": "http://example.com"
        }
        expected = "Python Developer | Компания: TechCorp | Зарплата: от 50000 до 70000 RUB | Ссылка: http://example.com"
        self.assertEqual(format_vacancy(vacancy), expected)

    def test_format_vacancy_no_salary(self):
        vacancy = {
            "name": "Python Developer",
            "company": "TechCorp",
            "salary_from": None,
            "salary_to": None,
            "salary_currency": None,
            "url": "http://example.com"
        }
        expected = "Python Developer | Компания: TechCorp | Зарплата: не указана | Ссылка: http://example.com"
        self.assertEqual(format_vacancy(vacancy), expected)

    def test_format_vacancy_from_only(self):
        vacancy = {
            "name": "Python Developer",
            "company": "TechCorp",
            "salary_from": 60000,
            "salary_to": None,
            "salary_currency": "RUB",
            "url": "http://example.com"
        }
        expected = "Python Developer | Компания: TechCorp | Зарплата: от 60000 RUB | Ссылка: http://example.com"
        self.assertEqual(format_vacancy(vacancy), expected)

    def test_format_vacancy_to_only(self):
        vacancy = {
            "name": "Python Developer",
            "company": "TechCorp",
            "salary_from": None,
            "salary_to": 80000,
            "salary_currency": "USD",
            "url": "http://example.com"
        }
        expected = "Python Developer | Компания: TechCorp | Зарплата: до 80000 USD | Ссылка: http://example.com"
        self.assertEqual(format_vacancy(vacancy), expected)