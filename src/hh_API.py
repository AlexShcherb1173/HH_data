# hh.ru API позволяет запросы по работодателю и /vacancies. Подберите 15 employer_id вручную (или заранее).


import requests
from typing import Dict, List, Optional

HH_API_BASE = "https://api.hh.ru"

class HHApiClient:
    """Клиент для публичного API hh.ru (ограниченная функциональность)."""

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def get_employer(self, employer_id: int) -> Dict:
        """Получить данные работодателя по id."""
        resp = self.session.get(f"{HH_API_BASE}/employers/{employer_id}")
        resp.raise_for_status()
        return resp.json()

    def get_vacancies_for_employer(self, employer_id: int, per_page: int = 100) -> List[Dict]:
        """Получить список вакансий работодателя (пагинация)."""
        results = []
        page = 0
        while True:
            params = {"employer_id": employer_id, "page": page, "per_page": per_page}
            resp = self.session.get(f"{HH_API_BASE}/vacancies", params=params)
            resp.raise_for_status()
            data = resp.json()
            results.extend(data.get("items", []))
            if page >= data.get("pages", 0) - 1:
                break
            page += 1
        return results