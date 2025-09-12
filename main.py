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

# import os
# from dotenv import load_dotenv
# from src.hh_api import HHApi
# from src.db_manager import DBManager, DBConfig
# from src.services import safe_get_salary
# # from src.db_config import DBConfig



# --- Компании для парсинга (5 IT-компаний) ---
# COMPANIES = [3529, 78638, 1740, 39305, 3776]  # Яндекс, Kaspersky, 1C, Лаборатория Касперского, Сбер
#
# def main():
#     load_dotenv()
#
#     config = DBConfig()
#     dbm = DBManager(config)
#     dbm.create_tables()
#
#     try:
#         with dbm._get_conn() as conn:
#             print("Подключение к БД успешно!")
#     except Exception as e:
#         print(f"Ошибка подключения: {e}")
#
#     db_config = DBConfig(
#         name=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT"),
#     )
#
#     dbm = DBManager(db_config)
#     dbm.create_tables()
#
#     api = HHApi(COMPANIES)
#     all_data = api.get_all_data()
#
#     # Заполняем таблицы
#     for block in all_data:
#         company = block["company"]
#         dbm.insert_company(company)
#
#         for vacancy in block["vacancies"]:
#             salary_from, salary_to, currency = safe_get_salary(vacancy)
#             vacancy["salary_from"], vacancy["salary_to"], vacancy["salary_currency"] = salary_from, salary_to, currency
#             dbm.insert_vacancy(vacancy, int(company["id"]))
#
#     # --- Пользовательский интерфейс ---
#     print("Компании и количество вакансий:")
#     for row in dbm.get_companies_and_vacancies_count():
#         print(f"{row['name']}: {row['vacancies_count']} вакансий")
#
#     print("\nСредняя зарплата по всем вакансиям:")
#     print(dbm.get_avg_salary())
#
#     keyword = input("\nВведите ключевое слово для поиска вакансий: ")
#     for row in dbm.get_vacancies_with_keyword(keyword):
#         print(f"{row['company']} | {row['vacancy']} | {row['salary_from']} - {row['salary_to']} {row['salary_currency']} | {row['url']}")
#
#
# if __name__ == "__main__":
#     main()

# def main():
#     load_dotenv()
#
#     db_config = DBConfig(
#         name=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         host=os.getenv("DB_HOST"),
#         port=int(os.getenv("DB_PORT"))
#     )
#
#     dbm = DBManager(db_config)
#     dbm.create_tables()
#     print("Таблицы созданы успешно!")
#
#     companies = dbm.get_companies_and_vacancies_count()
#     for c in companies:
#         print(c)
#
# if __name__ == "__main__":
#     main()

# from src.db_manager import DBManager, DBConfig
# from src.hh_api import HHApi
# import os
# from dotenv import load_dotenv
# from src.services import format_vacancy
#
#
# load_dotenv()
#
#
#
# def user_interface(dbm: DBManager):
#     """
#     Простой текстовый интерфейс для поиска вакансий по ключевому слову.
#     """
#     keyword = input("Введите ключевое слово для поиска вакансий: ").strip()
#     results = dbm.get_vacancies_with_keyword(keyword)
#     if not results:
#         print("Вакансии не найдены.")
#         return
#     for vac in results:
#         print(format_vacancy(vac))
#
# def main():
#     db_config = DBConfig(
#         name=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         host=os.getenv("DB_HOST"),
#         port=int(os.getenv("DB_PORT"))
#     )
#     dbm = DBManager(db_config)
#     dbm.create_tables()
#
#     hh = HHApi()
#     companies = hh.get_companies()  # топ-15 IT компаний
#     dbm.insert_companies(companies)
#
#     for c in companies:
#         vacancies = hh.get_vacancies_for_company(c["id"])
#         dbm.insert_vacancies(vacancies)
#
#     # Пример использования аналитики
#     print(dbm.get_companies_and_vacancies_count())
#     print(dbm.get_all_vacancies())
#
# if __name__ == "__main__":
#     main()

import os
from src.hh_api import HHApi
from src.db_manager import DBManager, DBConfig
from src.work_vacancies import parse_vacancies
from src.work_files import save_to_json, save_to_csv
from src. services import format_vacancy
from dotenv import load_dotenv
from tqdm import tqdm  # Для прогресс-бара

load_dotenv(encoding="utf-8")

def main():
    # --- Настройка подключения к базе ---
    db_config = DBConfig(
        name=os.getenv("DB_NAME", "hh_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432))
    )
    db = DBManager(db_config)
    db.create_tables()

    # --- Создание API клиента HH.ru ---
    hh = HHApi()

    # --- Ввод ключевого слова от пользователя ---
    keyword = input("Введите ключевое слово для поиска вакансий (по умолчанию IT): ").strip()
    if not keyword:
        keyword = "IT"

    print(f"\nИщем компании по ключевому слову '{keyword}'...")

    # --- Получаем компании и сохраняем их в БД ---
    companies = hh.get_companies(text=keyword)
    db.insert_companies(companies)
    print(f"Найдено компаний: {len(companies)}")

    all_vacancies = []

    # --- Получаем вакансии для каждой компании с прогресс-баром ---
    print("\nПолучаем вакансии для компаний...")
    for company in tqdm(companies, desc="Компании"):
        vacancies = hh.get_vacancies_for_company(company['id'])
        # parsed = parse_vacancies(vacancies)
        db.insert_vacancies(vacancies)
        all_vacancies.extend(vacancies)

    # --- Сохраняем данные в JSON и CSV ---
    os.makedirs("data", exist_ok=True)
    save_to_json("data/companies.json", companies)
    save_to_json("data/vacancies.json", all_vacancies)
    if all_vacancies:
        save_to_csv("data/companies.csv", companies, fieldnames=["id", "name"])
        save_to_csv(
            "data/vacancies.csv",
            all_vacancies,
            fieldnames=["vacancy_id", "name", "company_id", "salary_from", "salary_to", "salary_currency", "url"]
        )

    # --- Интерфейс поиска и отображения ---
    while True:
        print("\nВыберите действие:")
        print("1 - Показать все вакансии")
        print("2 - Показать вакансии с зарплатой выше средней")
        print("3 - Показать вакансии по ключевому слову")
        print("0 - Выйти")
        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            vacancies = db.get_all_vacancies()
            for v in vacancies:
                print(format_vacancy(v))

        elif choice == "2":
            vacancies = db.get_vacancies_with_higher_salary()
            for v in vacancies:
                print(format_vacancy(v))

        elif choice == "3":
            kw = input("Введите ключевое слово для поиска: ").strip()
            vacancies = db.get_vacancies_with_keyword(kw)
            if not vacancies:
                print("Вакансий не найдено.")
            else:
                for v in vacancies:
                    print(format_vacancy(v))

        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Некорректный ввод. Попробуйте снова.")

if __name__ == "__main__":
    main()