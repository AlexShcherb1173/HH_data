import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
from config import DB

class DBManager:
    """
    Менеджер для работы с базой hh_schema.
    """

    def __init__(self, db_config=DB):
        self._db_config = db_config

    def _get_conn(self):
        return psycopg2.connect(
            host=self._db_config.host,
            port=self._db_config.port,
            dbname=self._db_config.dbname,
            user=self._db_config.user,
            password=self._db_config.password
        )

    def create_tables(self):
        """Создать таблицы (если не существуют)."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                with open("db/create_db.sql", "r", encoding="utf-8") as f:
                    cur.execute(f.read())
            conn.commit()

    def upsert_company(self, company: Dict):
        """Вставить или обновить компанию по company_id."""
        sql = """
        INSERT INTO hh_schema.companies (company_id, name, area_name, url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (company_id) DO UPDATE
          SET name = EXCLUDED.name,
              area_name = EXCLUDED.area_name,
              url = EXCLUDED.url;
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (company["id"], company.get("name"), company.get("area", {}).get("name") if company.get("area") else None, company.get("site_url")))
            conn.commit()

    def upsert_vacancy(self, vacancy: Dict, company_id: int):
        """Вставить или обновить вакансию по vacancy_id."""
        salary = vacancy.get("salary") or {}
        sal_from = salary.get("from")
        sal_to = salary.get("to")
        sal_curr = salary.get("currency")
        sql = """
        INSERT INTO hh_schema.vacancies (vacancy_id, company_id, name, description, salary_from, salary_to, salary_currency, area_name, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            salary_from = EXCLUDED.salary_from,
            salary_to = EXCLUDED.salary_to,
            salary_currency = EXCLUDED.salary_currency,
            area_name = EXCLUDED.area_name,
            url = EXCLUDED.url;
        """
        desc = vacancy.get("snippet", {}).get("responsibility") or vacancy.get("name")
        area = vacancy.get("area", {}).get("name") if vacancy.get("area") else None
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    vacancy["id"],
                    company_id,
                    vacancy.get("name"),
                    desc,
                    sal_from,
                    sal_to,
                    sal_curr,
                    area,
                    vacancy.get("alternate_url")
                ))
            conn.commit()

    # ==== Запрошенные методы ====

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """
        Возвращает список всех компаний с количеством вакансий у каждой.
        """
        sql = """
        SELECT c.company_id, c.name, COUNT(v.vacancy_id) AS vacancies_count
        FROM hh_schema.companies c
        LEFT JOIN hh_schema.vacancies v ON c.company_id = v.company_id
        GROUP BY c.company_id, c.name
        ORDER BY vacancies_count DESC;
        """
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def get_all_vacancies(self) -> List[Dict]:
        """
        Список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки.
        """
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM hh_schema.vacancies v
        JOIN hh_schema.companies c ON v.company_id = c.company_id
        ORDER BY v.vacancy_id;
        """
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """
        Средняя зарплата по вакансиям. Берём среднее по (salary_from + salary_to)/2 для записей, где есть числа.
        """
        sql = """
        SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2.0) AS avg_salary
        FROM hh_schema.vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else None

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """Возвращает вакансии с зарплатой выше средней."""
        avg = self.get_avg_salary()
        if avg is None:
            return []
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM hh_schema.vacancies v
        JOIN hh_schema.companies c ON v.company_id = c.company_id
        WHERE ((COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from)) / 2.0) > %s
        ORDER BY (COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from)) / 2.0 DESC;
        """
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (avg,))
                return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """Все вакансии, в названии которых есть keyword (регистронезависимо)."""
        like_expr = f"%{keyword}%"
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy, v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM hh_schema.vacancies v
        JOIN hh_schema.companies c ON v.company_id = c.company_id
        WHERE v.name ILIKE %s
        ORDER BY v.vacancy_id;
        """
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (like_expr,))
                return cur.fetchall()