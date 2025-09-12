from typing import Dict, Optional, Tuple, Any


def safe_get_salary(salary: Optional[Dict]) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Безопасно извлекает значения зарплаты из словаря.
    :param salary: словарь, полученный из API HH (ключи 'from', 'to', 'currency')
    :return: кортеж (salary_from, salary_to, currency)"""
    # Функция принимает один аргумент salary, который может быть словарём (Dict) или None (Optional[Dict]).    #
    # Возвращает кортеж из трёх элементов:    #
    # salary_from — минимальная зарплата (Optional[float])    #
    # salary_to — максимальная зарплата (Optional[float])    #
    # currency — валюта зарплаты (Optional[str])

    # Если словарь salary пустой или равен None, возвращаем тройку None,
    # чтобы код не ломался при отсутствии данных о зарплате.
    if not salary:
        return None, None, None
    # Из словаря salary берём значения по ключам: "from" — минимальная зарплата, "to" — максимальная зарплата
    # "currency" — валюта. Если какого-то ключа нет, dict.get() вернёт None.
    return salary.get("from"), salary.get("to"), salary.get("currency")


def format_salary(salary_from: Optional[float], salary_to: Optional[float], currency: Optional[str]) -> str:
    """Форматирует зарплату для человекочитаемого вывода.
    :param salary_from: минимальная зарплата
    :param salary_to: максимальная зарплата
    :param currency: валюта
    :return: строка, например "от 100000 до 150000 RUB" или "не указана"""
    # Функция преобразует числовые данные о зарплате в человекочитаемый формат, учитывая,
    # что значения могут отсутствовать.
    # Функция принимает три аргумента: salary_from — минимальная зарплата (может быть None),
    # salary_to — максимальная зарплата (может быть None), currency — валюта зарплаты (может быть None).
    # Возвращает строку, которая удобно читается человеком.

    if salary_from is None and salary_to is None:
        return "не указана"  # Если оба значения зарплаты отсутствуют, возвращаем "не указана".
    if salary_from is not None and salary_to is not None:
        return f"от {salary_from} до {salary_to} {currency}"  # Если обе границы зарплаты заданы, возвращаем
        # диапазон, например: "от 100000 до 150000 RUB"
    if salary_from is not None:
        return f"от {salary_from} {currency}"  # Если только минимальная зарплата задана, возвращаем: "от 100000 RUB"
    return f"до {salary_to} {currency}"  # Если только максимальная зарплата задана, возвращаем: "до 150000 RUB"


def format_vacancy(vacancy: Dict[str, Any]) -> str:
    """Преобразует данные вакансии в строку для отображения пользователю.
    :param vacancy: словарь с данными вакансии
    :return: человекочитаемая строка"""
    # Превращает словарь вакансии в читабельную строку для удобного отображения пользователю.
    # Функция принимает один аргумент vacancy — словарь с информацией о вакансии.    #
    # Возвращает строку, удобную для отображения пользователю.

    # Извлекаем поля зарплаты из словаря: "salary_from", "salary_to", "salary_currency".    #
    # Вызываем функцию format_salary, которая преобразует их в человекочитаемый вид, например:
    # "от 100000 до 150000 RUB" или "не указана".

    # Формируем строку с ключевой информацией о вакансии:
    # Название вакансии (vacancy.get('name'))
    # Компания (vacancy.get('company'))
    # Зарплата (вывод из salary_str)
    # Ссылка на вакансию (vacancy.get('url'))
    return (
        f"{vacancy.get('name')} | Компания: {vacancy.get('company')} | "
        f"Зарплата: {format_salary(vacancy.get('salary_from'), vacancy.get('salary_to'), vacancy.get('salary_currency'))} | "
        f"Ссылка: {vacancy.get('url')}"
    )
