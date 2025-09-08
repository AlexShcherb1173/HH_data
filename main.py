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
from src.hh_api import HHApiClient
from src.db_manager import DBManager
from src.work_vacancies import VacanciesLoader
from src.get_api import get_top_russian_companies


def main() -> None:
    """        Основная функция: загрузка топ-15 компаний РФ."""
    try:
        employers = get_top_russian_companies(top_n=15)
    except RuntimeError as e:
        print(f"Ошибка: {e}")
        return

    # Оставляем только ID компаний
    COMPANIES = [emp["id"] for emp in employers]

    print("\n📌 ID компаний для загрузки вакансий:")
    print(COMPANIES)

    return COMPANIES


# if __name__ == "__main__":
#     COMPANIES = main()

def main():
    client = HHApiClient()
    dbm = DBManager()
    dbm.create_tables()

    loader = VacanciesLoader(client, dbm)
    loader.load_for_employers(COMPANIES)

    # Примеры использования DBManager
    print(dbm.get_companies_and_vacancies_count())
    print(dbm.get_avg_salary())
    print(len(dbm.get_vacancies_with_keyword("python")))

if __name__ == "__main__":
    main()