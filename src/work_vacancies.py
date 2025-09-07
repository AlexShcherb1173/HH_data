# Модуль обработки вакансий и загрузки


from it_api.hh_api import HHApiClient
from db_manager.db_manager import DBManager
from typing import List

class VacanciesLoader:
    """Класс для загрузки данных из hh.ru в БД."""

    def __init__(self, client: HHApiClient, dbm: DBManager):
        self.client = client
        self.dbm = dbm

    def load_for_employers(self, employer_ids: List[int]):
        for emp_id in employer_ids:
            try:
                emp = self.client.get_employer(emp_id)
                self.dbm.upsert_company(emp)
                vacancies = self.client.get_vacancies_for_employer(emp_id)
                for vac in vacancies:
                    self.dbm.upsert_vacancy(vac, emp_id)
            except Exception as e:
                # логирование можно добавить
                print(f"Failed to process employer {emp_id}: {e}")