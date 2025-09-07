def safe_get_salary(vacancy: dict):
    s = vacancy.get("salary")
    if not s:
        return None, None, None
    return s.get("from"), s.get("to"), s.get("currency")