# напишем тесты для DBManager с использованием unittest.mock, чтобы не трогать настоящую базу данных.
# Мы будем мокать psycopg2.connect и курсоры.
# Что делают эти тесты#
# Мокают psycopg2.connect, чтобы не подключаться к настоящей БД.#
# Проверяют, что execute и commit вызываются.#
# Проверяют, что методы, возвращающие данные (fetchall/fetchone), корректно обрабатывают результат.#
# get_vacancies_with_higher_salary дополнительно мокает get_avg_salary, чтобы тест был изолированным.
# Для всех with self._get_conn() as conn: добавлен mock_connect.return_value.__enter__.return_value = mock_conn.#
# Для курсоров: mock_conn.cursor.return_value.__enter__.return_value = mock_cursor.#
# Методы с fetchall() и fetchone() возвращают реальные списки/числа, а не MagicMock.#


import unittest
from unittest.mock import MagicMock, patch

from src.db_manager import DBConfig, DBManager


class TestDBManager(unittest.TestCase):
    def setUp(self) -> None:
        config = DBConfig(name="testdb", user="user", password="pass", host="localhost", port=5432)
        self.db_manager = DBManager(config)

    @patch("psycopg2.connect")
    def test_create_tables(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Настраиваем контекстный менеджер
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        self.db_manager.create_tables()

        self.assertTrue(mock_cursor.execute.called)
        mock_conn.commit.assert_called_once()

    @patch("psycopg2.connect")
    def test_insert_companies(self, mock_connect: MagicMock) -> None:
        companies: list[dict[str, str | int]] = [{"id": 1, "name": "Company1"}, {"id": 2, "name": "Company2"}]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        self.db_manager.insert_companies(companies)

        self.assertEqual(mock_cursor.execute.call_count, len(companies))
        mock_conn.commit.assert_called_once()

    @patch("psycopg2.connect")
    def test_insert_vacancies(self, mock_connect: MagicMock) -> None:
        vacancies = [
            {
                "vacancy_id": 1,
                "company_id": 1,
                "name": "Dev",
                "salary_from": 1000,
                "salary_to": 2000,
                "salary_currency": "USD",
                "url": "http://example.com",
            }
        ]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        self.db_manager.insert_vacancies(vacancies)

        self.assertEqual(mock_cursor.execute.call_count, len(vacancies))
        mock_conn.commit.assert_called_once()

    @patch("psycopg2.connect")
    def test_get_companies_and_vacancies_count(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        expected_result = [{"company_id": 1, "name": "Company1", "vacancies_count": 5}]

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = expected_result

        result = self.db_manager.get_companies_and_vacancies_count()

        self.assertEqual(result, expected_result)

    @patch("psycopg2.connect")
    def test_get_all_vacancies(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        expected_result = [{"vacancy_id": 1, "company": "Company1", "vacancy": "Dev"}]

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = expected_result

        result = self.db_manager.get_all_vacancies()

        self.assertEqual(result, expected_result)

    @patch("psycopg2.connect")
    def test_get_avg_salary(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1500.0]

        avg = self.db_manager.get_avg_salary()

        self.assertEqual(avg, 1500.0)

    @patch("psycopg2.connect")
    @patch.object(DBManager, "get_avg_salary", return_value=1500.0)
    def test_get_vacancies_with_higher_salary(self, mock_avg: MagicMock, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        expected_result = [{"vacancy_id": 1, "company": "Company1", "vacancy": "Dev"}]

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = expected_result

        result = self.db_manager.get_vacancies_with_higher_salary()

        self.assertEqual(result, expected_result)

    @patch("psycopg2.connect")
    def test_get_vacancies_with_keyword(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        expected_result = [{"vacancy_id": 1, "company": "Company1", "vacancy": "Python Dev"}]

        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = expected_result

        result = self.db_manager.get_vacancies_with_keyword("Python")

        self.assertEqual(result, expected_result)
