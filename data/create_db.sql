-- Создание схемы/таблиц для проекта
-- Выполнить от имени суперпользователя или пользователя с правами
-- Bоспользуемся company_id и vacancy_id как целые, совпадающие с id из API hh.ru — это удобно для обновлений.

CREATE SCHEMA IF NOT EXISTS hh_schema;

-- Таблица работодателей (companies)
CREATE TABLE IF NOT EXISTS hh_schema.companies (
    company_id     INTEGER PRIMARY KEY,
    name           VARCHAR NOT NULL,
    area_name      VARCHAR,
    url            TEXT,
    created_at     TIMESTAMP DEFAULT now()
);

-- Таблица вакансий (vacancies)
CREATE TABLE IF NOT EXISTS hh_schema.vacancies (
    vacancy_id     INTEGER PRIMARY KEY,
    company_id     INTEGER NOT NULL REFERENCES hh_schema.companies(company_id) ON DELETE CASCADE,
    name           VARCHAR NOT NULL,
    description    TEXT,
    salary_from    INTEGER,
    salary_to      INTEGER,
    salary_currency VARCHAR(10),
    area_name      VARCHAR,
    url            TEXT,
    created_at     TIMESTAMP DEFAULT now()
);