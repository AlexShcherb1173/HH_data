from it_api.hh_api import HHApiClient
from db_manager.db_manager import DBManager
from work_vacancies.vacancies_processor import VacanciesLoader

# Список из 15 employer_id (пример — подставьте реальные ids)
COMPANIES = [123, 456, 789, 1011, 1213, 1415, 1617, 1819, 2021, 2223, 2425, 2627, 2829, 3031, 3233]

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