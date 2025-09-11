from typing import Any, Dict, Optional, Tuple


def safe_get_salary(vacancy: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Аккуратно извлекает salary из вакансии hh.ru.
    Возвращает (salary_from, salary_to, currency).
    """
    s = vacancy.get("salary")
    if not s:
        return None, None, None
    return s.get("from"), s.get("to"), s.get("currency")