# from src.hh_api import HHApiClient
# from src.db_manager import DBManager
# from src.work_vacancies import VacanciesLoader

# Список из 15 employer_id (пример — подставьте реальные ids)
# COMPANIES = [123, 456, 789, 1011, 1213, 1415, 1617, 1819, 2021, 2223, 2425, 2627, 2829, 3031, 3233]
#
# def main():
#     client = HHApiClient()
#     dbm = DBManager()
#     dbm.create_tables()
#
#     loader = VacanciesLoader(client, dbm)
#     loader.load_for_employers(COMPANIES)
#
#     # Примеры использования DBManager
#     print(dbm.get_companies_and_vacancies_count())
#     print(dbm.get_avg_salary())
#     print(len(dbm.get_vacancies_with_keyword("python")))
#
# if __name__ == "__main__":
#     main()




# from src.hh_api import HHApiClient
# from src.db_manager import DBManager
# from src.work_vacancies import VacanciesLoader
# from src.get_api import get_top_russian_companies
#
#
# def company_sheet() -> None:
#     """Основная функция: загрузка топ-15 компаний РФ."""
#     try:
#         employers = get_top_russian_companies(top_n=15)
#     except RuntimeError as e:
#         print(f"Ошибка: {e}")
#         return
#
#     # Оставляем только ID компаний
#     COMPANIES = [emp["id"] for emp in employers]
#
#     # print("\n📌 ID компаний для загрузки вакансий:")
#     # print(COMPANIES)
#
#     return COMPANIES
#
#
# if __name__ == "__main__":
#      COMPANIES: None = company_sheet()
#
# def main():
#     client = HHApiClient()
#     dbm = DBManager()
#     dbm.create_tables()
#
#     loader = VacanciesLoader(client, dbm)
#     loader.load_for_employers(COMPANIES)
#
#     # Примеры использования DBManager
#     print(dbm.get_companies_and_vacancies_count())
#     print(dbm.get_avg_salary())
#     print(len(dbm.get_vacancies_with_keyword("python")))
#
# if __name__ == "__main__":
#     main()

import os
from dotenv import load_dotenv
from src.hh_api import HHApi
from src.db_manager import DBManager, DBConfig
from src.services import safe_get_salary
from src.db_config import DBConfig



# --- Компании для парсинга (5 IT-компаний) ---
COMPANIES = [3529, 78638, 1740, 39305, 3776]  # Яндекс, Kaspersky, 1C, Лаборатория Касперского, Сбер

def main():
    load_dotenv()

    config = DBConfig()
    dbm = DBManager(config)
    dbm.create_tables()

    try:
        with dbm._get_conn() as conn:
            print("Подключение к БД успешно!")
    except Exception as e:
        print(f"Ошибка подключения: {e}")

    db_config = DBConfig(
        name=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

    dbm = DBManager(db_config)
    dbm.create_tables()

    api = HHApi(COMPANIES)
    all_data = api.get_all_data()

    # Заполняем таблицы
    for block in all_data:
        company = block["company"]
        dbm.insert_company(company)

        for vacancy in block["vacancies"]:
            salary_from, salary_to, currency = safe_get_salary(vacancy)
            vacancy["salary_from"], vacancy["salary_to"], vacancy["salary_currency"] = salary_from, salary_to, currency
            dbm.insert_vacancy(vacancy, int(company["id"]))

    # --- Пользовательский интерфейс ---
    print("Компании и количество вакансий:")
    for row in dbm.get_companies_and_vacancies_count():
        print(f"{row['name']}: {row['vacancies_count']} вакансий")

    print("\nСредняя зарплата по всем вакансиям:")
    print(dbm.get_avg_salary())

    keyword = input("\nВведите ключевое слово для поиска вакансий: ")
    for row in dbm.get_vacancies_with_keyword(keyword):
        print(f"{row['company']} | {row['vacancy']} | {row['salary_from']} - {row['salary_to']} {row['salary_currency']} | {row['url']}")


if __name__ == "__main__":
    main()