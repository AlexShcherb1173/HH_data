# hh.ru API позволяет запросы по работодателю и /vacancies.
# использует requests, реализует класс для получения компаний и вакансий
import os
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
load_dotenv(encoding="utf-8")


class HHApi:
    """Класс для взаимодействия с API hh.ru."""

    BASE_URL = os.getenv("HH_API_URL", "https://api.hh.ru")

    def __init__(self, employers: List[int]) -> None:
        self.employers = employers

    def get_company_info(self, employer_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о компании по её employer_id"""
        url = f"{self.BASE_URL}/employers/{employer_id}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """Получает список вакансий компании"""
        url = f"{self.BASE_URL}/vacancies"
        params = {"employer_id": employer_id, "per_page": 100}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        return []

    def get_all_data(self) -> List[Dict[str, Any]]:
        """Возвращает данные о компаниях и их вакансиях"""
        data = []
        for eid in self.employers:
            company = self.get_company_info(eid)
            vacancies = self.get_vacancies(eid)
            if company:
                data.append({"company": company, "vacancies": vacancies})
        return data