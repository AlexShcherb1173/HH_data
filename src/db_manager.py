import psycopg2
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class DBConfig:
    name: str
    user: str
    password: str
    host: str
    port: str

class DBManager:
    """Класс для работы с PostgreSQL"""

    def __init__(self, db_config: DBConfig):
        self._db_config = db_config

    def _get_conn(self) -> psycopg2.extensions.connection:
        """Создаёт и возвращает подключение к БД PostgreSQL."""
        return psycopg2.connect(
            dbname=self._db_config.name,
            user=self._db_config.user,
            password=self._db_config.password,
            host=self._db_config.host,
            port=self._db_config.port,
        )

    def create_tables(self) -> None:
        """Создаёт таблицы компаний и вакансий"""
        sql_companies = """
        CREATE TABLE IF NOT EXISTS companies (
            company_id INT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT);
        """

        sql_vacancies = """
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id INT PRIMARY KEY,
            company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            salary_from NUMERIC,
            salary_to NUMERIC,
            salary_currency VARCHAR(10),
            url TEXT);
        """

        with self._get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql_companies)
            cur.execute(sql_vacancies)
            conn.commit()

    def insert_company(self, company: Dict) -> None:
        """Вставляет компанию"""
        sql = """
        INSERT INTO companies (company_id, name, url)
        VALUES (%s, %s, %s)
        ON CONFLICT (company_id) DO UPDATE SET
            name = EXCLUDED.name,
            url = EXCLUDED.url;
        """
        with self._get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (int(company["id"]), company["name"], company.get("alternate_url")))
            conn.commit()

    def insert_vacancy(self, vacancy: Dict, company_id: int) -> None:
        """Вставляет вакансию"""
        salary_from, salary_to, currency = vacancy.get("salary_from"), vacancy.get("salary_to"), vacancy.get("salary_currency")
        sql = """
        INSERT INTO vacancies (vacancy_id, company_id, name, salary_from, salary_to, salary_currency, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO UPDATE SET
            name = EXCLUDED.name,
            salary_from = EXCLUDED.salary_from,
            salary_to = EXCLUDED.salary_to,
            salary_currency = EXCLUDED.salary_currency,
            url = EXCLUDED.url;
        """
        with self._get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (
                int(vacancy["id"]),
                company_id,
                vacancy["name"],
                salary_from,
                salary_to,
                currency,
                vacancy["alternate_url"],
            ))
            conn.commit()

    # --- Методы для аналитики ---

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        sql = """
        SELECT c.company_id, c.name, COUNT(v.vacancy_id) AS vacancies_count
        FROM companies c
        LEFT JOIN vacancies v ON c.company_id = v.company_id
        GROUP BY c.company_id, c.name
        ORDER BY vacancies_count DESC;
        """
        with self._get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Dict]:
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM vacancies v
        JOIN companies c ON v.company_id = c.company_id
        ORDER BY v.vacancy_id;
        """
        with self._get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        sql = """
        SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2.0) AS avg_salary
        FROM vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        with self._get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
            return row[0] if row else None

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        avg = self.get_avg_salary()
        if avg is None:
            return []
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM vacancies v
        JOIN companies c ON v.company_id = c.company_id
        WHERE ((COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from)) / 2.0) > %s
        ORDER BY (COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from)) / 2.0 DESC;
        """
        with self._get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (avg,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        like_expr = f"%{keyword}%"
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM vacancies v
        JOIN companies c ON v.company_id = c.company_id
        WHERE v.name ILIKE %s
        ORDER BY v.vacancy_id;
        """
        with self._get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (like_expr,))
            return cur.fetchall()









