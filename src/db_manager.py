import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass   # Декоратор, который автоматически генерирует для класса:
             # __init__ (конструктор),
             # __repr__ (удобное строковое представление),
             # __eq__ (сравнение объектов).
class DBConfig:
    """Класс описывает конфигурацию подключения к базе данных."""
    name: str      # имя базы данных
    user: str      # пользователь PostgreSQL (например "postgres").
    password: str  # password: str → пароль пользователя.
    host: str      # host: str → адрес сервера БД (например "localhost" или "127.0.0.1").
    port: int      # порт PostgreSQL (обычно 5432).

class DBManager:
    """Класс для работы с базой данных PostgreSQL для хранения и чтения информации о компаниях и вакансиях с HH.ru."""
    # Прослойка» между Python-кодом и PostgreSQL. Он получает конфигурацию (DBConfig) и создаёт подключения к базе.

    def __init__(self, db_config: DBConfig):  # Конструктор принимает объект DBConfig
        self._db_config = db_config  # Эти параметры сохраняются в _db_config, чтобы потом использовать при подключении.

    def _get_conn(self) -> psycopg2.extensions.connection:
        """Вспомогательный метод «для внутреннего использования». Возвращает подключение к базе данных."""
        return psycopg2.connect(                   # Здесь используются все параметры из DBConfig.
            dbname=self._db_config.name,
            user=self._db_config.user,
            password=self._db_config.password,
            host=self._db_config.host,
            port=self._db_config.port
        )                                         # И возвращает объект подключения connection,
                                                  # через который можно создавать курсоры и выполнять SQL-запросы.

    def create_tables(self):
        """Создает таблицы companies и vacancies в схеме hh_schema."""
        # Это метод класса DBManager. Он нужен для инициализации структуры базы данных:
        # Cоздаёт схему и таблицы, если их ещё нет
        # Метод гарантирует, что в базе данных появится схема hh_schema с двумя таблицами:
        # companies (компании), vacancies (вакансии, связанные с компаниями).
        # После этого можно загружать данные из API hh.ru и сохранять их напрямую в эти таблицы.

        # SQL-скрипт.
        # CREATE SCHEMA IF NOT EXISTS hh_schema; → создаётся схема hh_schema, если её ещё нет.
        # CREATE TABLE IF NOT EXISTS hh_schema.companies(...) → создаётся таблица компаний:
        #     company_id BIGINT PRIMARY KEY — уникальный идентификатор компании(например, из API hh.ru).
        #     name VARCHAR(255) NOT NULL — название компании.
        # CREATE TABLE IF NOT EXISTS hh_schema.vacancies(...) → создаётся таблица вакансий:
        #     vacancy_id BIGINT PRIMARY KEY — уникальный ID вакансии.
        #     company_id BIGINT REFERENCES hh_schema.companies(company_id) — внешний ключ(ссылается на компанию, у
        #                                                                    которой опубликована вакансия).
        #     name VARCHAR(255) NOT NULL — название вакансии.
        #     salary_from NUMERIC, salary_to NUMERIC — зарплата «от» и «до».
        #     salary_currency VARCHAR(10) — валюта(например, RUR, USD).
        #     url TEXT — ссылка на вакансию.
        sql = """                               
        CREATE SCHEMA IF NOT EXISTS hh_schema;     

        CREATE TABLE IF NOT EXISTS hh_schema.companies (
            company_id BIGINT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS hh_schema.vacancies (
            vacancy_id BIGINT PRIMARY KEY,
            company_id BIGINT REFERENCES hh_schema.companies(company_id),
            name VARCHAR(255) NOT NULL,
            salary_from NUMERIC,
            salary_to NUMERIC,
            salary_currency VARCHAR(10),
            url TEXT
        );
        """
        with self._get_conn() as conn:  # создаётся соединение с базой.
            with conn.cursor() as cur:  # создаётся курсор для выполнения SQL-запросов.
                cur.execute(sql)        # выполняется SQL-скрипт.
                conn.commit()           # фиксируются изменения.

    def insert_companies(self, companies: List[Dict]):
        """Сохраняет список компаний в БД."""
        # Метод принимает список словарей (companies), где у каждой компании есть хотя бы два поля:
        # id — идентификатор компании (из API hh.ru), name — название компании.
        # Задача метода — сохранить этот список в таблицу hh_schema.companies.
        # Метод получает список компаний (например, из API hh.ru) и добавляет их в таблицу hh_schema.companies.
        # Если компания с таким ID уже есть, она не дублируется.

        # Это SQL-шаблон:
        # INSERT INTO hh_schema.companies (company_id, name) → вставить данные в таблицу companies.
        # VALUES (%s, %s) → вместо %s подставятся реальные значения (id и name).
        # ON CONFLICT (company_id) DO NOTHING → если в таблице уже есть компания с таким company_id,
        # то ошибка не будет выброшена, вставка просто пропускается.
        sql = """
        INSERT INTO hh_schema.companies (company_id, name)
        VALUES (%s, %s)
        ON CONFLICT (company_id) DO NOTHING;
        """
        with self._get_conn() as conn:                     # открываем подключение к базе.
            with conn.cursor() as cur:                     # cоздаём курсор для выполнения SQL.
                for c in companies:                        # идём по списку компаний.
                    cur.execute(sql, (c["id"], c["name"])) # вставляем компанию в таблицу (подставляем id и название).
                conn.commit()                              # фиксируем изменения, чтобы данные сохранились.

    def insert_vacancies(self, vacancies: List[Dict]):
        """Сохраняет список вакансий в БД."""
        # Метод принимает список вакансий (vacancies), где каждая вакансия — это словарь (Dict).

        # SQL-шаблон:        #
        # INSERT INTO → вставляем данные в таблицу vacancies.        #
        # %s → плейсхолдеры (значения подставятся через Python).        #
        # ON CONFLICT (vacancy_id) DO NOTHING; → если вакансия с таким vacancy_id уже есть, ошибка не произойдёт,
        # а строка просто не будет добавлена (избежание дублей).
        sql = """
        INSERT INTO hh_schema.vacancies
        (vacancy_id, company_id, name, salary_from, salary_to, salary_currency, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO NOTHING;
        """
        with self._get_conn() as conn:                  # Открываем соединение с БД.
            with conn.cursor() as cur:                  # cоздаём курсор для выполнения SQL.
                for v in vacancies:                     # идём по списку компаний.
                    salary_from = v.get("salary_from")  # Используем .get() вместо v["..."],
                                                        # чтобы избежать ошибки KeyError, если вдруг ключа нет.
                    salary_to = v.get("salary_to")      # чтобы избежать ошибки KeyError, если вдруг ключа нет.
                    salary_currency = v.get("salary_currency")    # (например, не всегда зарплата указана в HH API).
                    cur.execute(sql, (                  # Подставляем значения конкретной вакансии в SQL-запрос.
                        v["vacancy_id"],
                        v["company_id"],
                        v["name"],
                        salary_from,                   # Если поля salary_from,
                        salary_to,                     # salary_to или salary_currency пустые,
                        salary_currency,               # в БД пойдут NULL
                        v["url"]
                    ))
                conn.commit()                          # Подтверждаем изменения

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """Возвращает список всех компаний с количеством вакансий у каждой, включая компании без вакансий,
           и сортирует их по количеству вакансий от большего к меньшему."""
        # Метод класса DBManager. Возвращает список словарей (List[Dict]),
        # где каждый словарь — это компания с полями company_id, name и vacancies_count.

        # SQL-запрос:        #
        # Выбирает: company_id и name из таблицы companies.        #
        # Считает количество вакансий (COUNT(v.vacancy_id)) для каждой компании → vacancies_count.        #
        # LEFT JOIN: соединяем companies и vacancies по company_id.        #
        # LEFT JOIN гарантирует, что компании без вакансий тоже попадут в результат (кол-во вакансий будет 0).        #
        # GROUP BY: группируем по компании, чтобы COUNT корректно посчитал вакансии.        #
        # ORDER BY vacancies_count DESC: сортируем по количеству вакансий по убыванию.
        sql = """
        SELECT c.company_id, c.name, COUNT(v.vacancy_id) AS vacancies_count
        FROM hh_schema.companies c
        LEFT JOIN hh_schema.vacancies v ON c.company_id = v.company_id
        GROUP BY c.company_id, c.name
        ORDER BY vacancies_count DESC;
        """
        with self._get_conn() as conn:                              # Открываем соединение с БД
            with conn.cursor(cursor_factory=RealDictCursor) as cur: # Создаём курсор с RealDictCursor →
                                                  # возвращает строки как словари (ключи — имена столбцов).
                cur.execute(sql)                                    # Выполняем SQL-запрос.
                return cur.fetchall()                          # возвращает все строки результата как список словарей.

    def get_all_vacancies(self) -> List[Dict]:
        """Список всех вакансий с указанием названия компании, вакансии, зарплаты и ссылки."""
        # Метод класса DBManager. Возвращает список словарей (List[Dict]), где каждый словарь —
        # это одна вакансия с данными о компании, названии вакансии, зарплате и ссылке.
        # Метод возвращает все вакансии из БД с информацией о: компании, названии вакансии,
        # зарплате (от, до, валюта), ссылке на вакансию.

        # SQL - запрос выбирает:
        # v.vacancy_id — уникальный идентификатор вакансии.
        # c.name AS company — название компании, где AS company задаёт имя поля в результате.
        # v.name AS vacancy — название вакансии.
        # v.salary_from, v.salary_to, v.salary_currency — диапазон зарплаты и валюта.
        # v.url — ссылка на вакансию.
        # JOIN: соединяем таблицу vacancies с таблицей companies по company_id, чтобы получить имя компании
        #       для каждой вакансии.
        # ORDER BY v.vacancy_id: сортируем результат по идентификатору вакансии.\
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy,
               v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM hh_schema.vacancies v
        JOIN hh_schema.companies c ON v.company_id = c.company_id
        ORDER BY v.vacancy_id;
        """
        with self._get_conn() as conn:                              # Открываем соединение с базой данных
            with conn.cursor(cursor_factory=RealDictCursor) as cur: # Создаём курсор с RealDictCursor →
                                                 # строки будут возвращаться как словари (ключи — имена столбцов).
                cur.execute(sql)                                    # Выполняем SQL-запрос
                return cur.fetchall()                        # возвращает все строки результата как список словарей.

    def get_avg_salary(self) -> Optional[float]:
        """Средняя зарплата по вакансиям, берём среднее (salary_from + salary_to)/2 там, где есть числа."""
        # Метод класса DBManager. Возвращает среднюю зарплату по всем вакансиям в базе.

    #  SQL-запрос делает следующее:
     # COALESCE(salary_from, salary_to) — если salary_from NULL, берём salary_to.
    # COALESCE(salary_to, salary_from) — если salary_to NULL, берём salary_from.
    # (COALESCE(...) + COALESCE(...))/2.0 — вычисляем среднюю зарплату для каждой вакансии (среднее между from и to).
    # AVG(...) — вычисляем среднее значение по всем вакансиям.
    # WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL — исключаем вакансии без данных о зарплате.
        sql = """
        SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from))/2.0) AS avg_salary
        FROM hh_schema.vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        with self._get_conn() as conn:          # Открываем соединение с БД.
            with conn.cursor() as cur:          # Создаём обычный курсор.
                cur.execute(sql)                # Выполняем SQL-запрос.
                row = cur.fetchone()            # возвращает одну строку результата (в данном случае среднее значение).
                return row[0] if row else None  # значение средней зарплаты. Если строка отсутствует, возвращаем None.

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """Возвращает вакансии с зарплатой выше средней."""
    # Метод класса DBManager.Возвращает список вакансий, у которых средняя зарплата выше средней по всем вакансиям.
    # Метод возвращает все вакансии с зарплатой выше средней по базе, включая: ID вакансии, название компании,
    # название вакансии, диапазон зарплаты и валюту, ссылку на вакансию.

        avg = self.get_avg_salary()  # Получаем среднюю зарплату по всем вакансиям с помощью метода get_avg_salary().
        if avg is None:  # Если вакансий с зарплатой нет (avg is None), возвращаем пустой список.
            return []

        # SQL-запрос:
        # Берёт вакансии и их компании (JOIN hh_schema.companies).
        # COALESCE(v.salary_from, v.salary_to) и
        # COALESCE(v.salary_to, v.salary_from) — безопасно берём значения зарплат, если одно из них NULL.
        # Среднее (salary_from + salary_to)/2.
        # WHERE … > %s — фильтруем вакансии, средняя зарплата которых выше переданного значения (avg).
        # ORDER BY … DESC — сортируем по средней зарплате по убыванию.
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy,
               v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM hh_schema.vacancies v
        JOIN hh_schema.companies c ON v.company_id = c.company_id
        WHERE ((COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from))/2.0) > %s
        ORDER BY ((COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from))/2.0) DESC;
        """
        with self._get_conn() as conn:         # Создаём подключение к базе.
            with conn.cursor(cursor_factory=RealDictCursor) as cur: # Используем RealDictCursor, чтобы возвращать
                                                      # результат в виде списка словарей (ключи — имена столбцов).
                cur.execute(sql, (avg,))       # выполняем SQL, подставляя среднюю зарплату.
                return cur.fetchall()          # получаем все строки результата.

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """Все вакансии, в названии которых есть keyword (регистронезависимо)."""
        # Метод класса DBManager. Возвращает список вакансий, где в названии вакансии встречается
        # заданное ключевое слово. Параметр keyword: str — слово для поиска.
        # Метод ищет все вакансии по ключевому слову в названии, без учёта регистра, и возвращает
        # подробную информацию по каждой: ID, компания, название вакансии, зарплата и ссылка.

        like_expr = f"%{keyword}%"  # Формируем выражение для SQL LIKE.

        # SQL-запрос:        #
        # Берём вакансии и их компании (JOIN hh_schema.companies).        #
        # v.name ILIKE %s — ищем вакансии, где название содержит keyword, регистронезависимо         #
        # Сортируем по vacancy_id.
        sql = """
        SELECT v.vacancy_id, c.name AS company, v.name AS vacancy,
               v.salary_from, v.salary_to, v.salary_currency, v.url
        FROM hh_schema.vacancies v
        JOIN hh_schema.companies c ON v.company_id = c.company_id
        WHERE v.name ILIKE %s
        ORDER BY v.vacancy_id;
        """
        with self._get_conn() as conn:  # Создаём подключение к базе
            with conn.cursor(cursor_factory=RealDictCursor) as cur: # Используем RealDictCursor, чтобы результат
                                                                  # был списком словарей (ключи — имена столбцов).
                cur.execute(sql, (like_expr,))  # выполняем SQL, передавая выражение для поиска.
                return cur.fetchall()  # возвращаем все найденные вакансии.








