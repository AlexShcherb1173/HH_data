# Запрашивает у API hh.ru список работодателей, фильтруя по ключевому слову.
# Возвращает список словарей с базовой информацией (id, name, url и др.).
# Можно потом использовать id компании для получения вакансий.


import requests
from typing import List, Dict

BASE_URL = "https://api.hh.ru"


def get_top_employers(query: str, top_n: int = 15) -> List[Dict]:
    """
    Получает топ-N компаний по ключевому слову с hh.ru.

    :param query: поисковый запрос (например, 'банк', 'it', 'python')
    :param top_n: сколько компаний вернуть (по умолчанию 15)
    :return: список словарей с id, названием и количеством вакансий
    """
    url = f"{BASE_URL}/employers"
    params = {"text": query, "per_page": top_n}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"Ошибка при запросе к API hh.ru: {response.status_code}, {response.text}"
        )

    data = response.json()
    employers = data.get("items", [])

    # Сократим до нужного количества
    result = []
    for emp in employers[:top_n]:
        result.append({
            "id": emp["id"],
            "name": emp["name"],
            "open_vacancies": emp.get("open_vacancies", 0),
        })
    return result