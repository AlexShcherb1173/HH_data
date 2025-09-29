import os
import time
import requests
from src.hh_api import HHApi
from src.db_manager import DBManager, DBConfig
from src.work_files import save_to_json, save_to_csv
from src.services import format_vacancy
from dotenv import load_dotenv
from tqdm import tqdm

#load_dotenv(encoding="utf-8", override=True)
def load_env_safe() -> None:
    try:
        load_dotenv(encoding="utf-8", override=True)
    except UnicodeDecodeError as e:
        print(f"Предупреждение: .env не в UTF-8 ({e}). Повторная загрузка без encoding...")
        load_dotenv(override=True)


def sanitize_env(val: str | None) -> str | None:
    if val is None:
        return None
    # Удаляем невидимые и неразрывные пробелы/кавычки
    return (
        val.replace("\u00A0", " ")  # NBSP
           .replace("\u200B", "")   # zero-width space
           .replace("“", '"').replace("”", '"').replace("’", "'")
           .strip()
    )
load_env_safe()

def safe_hh_request(func, *args, retries=3, delay=2, **kwargs):
    """
    Обёртка для безопасного вызова методов HHApi с повтором при ошибках соединения.
    :param func: метод HHApi
    :param args: позиционные аргументы для метода
    :param retries: количество попыток
    :param delay: задержка между попытками (сек)
    :param kwargs: именованные аргументы для метода
    :return: результат функции или пустой список при неудаче
    """
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к HH API: {e}. Попытка {attempt} из {retries}...")
            if attempt < retries:
                time.sleep(delay)
            else:
                print("Не удалось получить данные после нескольких попыток.")
                return []

def wait_for_db(db: DBManager, retries: int = 5, delay: float = 1.5) -> bool:
    """
    Пытается получить соединение с БД несколько раз, чтобы дождаться готовности сервера.
    Возвращает True при успехе, False при неудаче.
    """
    for attempt in range(1, retries + 1):
        try:
            # быстрый ping через открытие и закрытие соединения
            with db._get_conn() as conn:  # type: ignore[attr-defined]
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            return True
        except Exception as e:
            print(f"Не удалось подключиться к БД (попытка {attempt}/{retries}): {e}")
            time.sleep(delay)
    return False


def main():
    # Читаем env и санитизируем
    name = sanitize_env(os.getenv("DB_NAME")) or "hh_db"
    user = sanitize_env(os.getenv("DB_USER")) or "postgres"
    password = sanitize_env(os.getenv("DB_PASSWORD")) or "postgres"
    host = sanitize_env(os.getenv("DB_HOST")) or "localhost"
    port_str = sanitize_env(os.getenv("DB_PORT")) or "5432"
    try:
        port = int(port_str)
    except ValueError:
        print(f"Некорректный DB_PORT='{port_str}', используется 5432")
        port = 5432

    # --- Настройка подключения к базе ---
    db_config = DBConfig(
        name=os.getenv("DB_NAME", "hh_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432))
    )
    db = DBManager(db_config)

    # Перед созданием таблиц — дождаться доступности БД
    if not wait_for_db(db):
        print(
            "База данных недоступна. Проверьте, что PostgreSQL запущен и параметры подключения корректны:\n"
            f"DB_HOST={db_config.host} DB_PORT={db_config.port} DB_NAME={db_config.name} "
            f"DB_USER={db_config.user}"
        )
        return

    db.create_tables()

    # --- Создание API клиента HH.ru ---
    hh = HHApi()

    # --- Ввод ключевого слова ---
    keyword = input("Введите ключевое слово для поиска вакансий (по умолчанию IT): ").strip() or "IT"

    print(f"\nИщем компании по ключевому слову '{keyword}'...")

    # --- Получаем компании через безопасный вызов ---
    companies = safe_hh_request(hh.get_companies, text=keyword)
    if not companies:
        print(f"По ключевому слову '{keyword}' компании не найдены. Завершение программы.")
        return

    db.insert_companies(companies)
    print(f"Найдено компаний: {len(companies)}")

    all_vacancies = []

    # --- Получаем вакансии для каждой компании с прогресс-баром ---
    print("\nПолучаем вакансии для компаний...")
    for company in tqdm(companies, desc="Компании"):
        vacancies = safe_hh_request(hh.get_vacancies_for_company, company['id'])
        if vacancies:
            db.insert_vacancies(vacancies)
            all_vacancies.extend(vacancies)

    # --- Сохраняем данные ---
    os.makedirs("data", exist_ok=True)
    save_to_json("data/companies.json", companies)
    save_to_json("data/vacancies.json", all_vacancies)
    if companies:
        save_to_csv("data/companies.csv", companies, fieldnames=["id", "name"])
    if all_vacancies:
        save_to_csv(
            "data/vacancies.csv",
            all_vacancies,
            fieldnames=["vacancy_id", "name", "company_id", "salary_from", "salary_to", "salary_currency", "url"]
        )

    # --- Интерфейс пользователя ---
    while True:
        print("\nВыберите действие:")
        print("1 - Показать все вакансии")
        print("2 - Показать вакансии с зарплатой выше средней")
        print("3 - Показать вакансии по ключевому слову")
        print("0 - Выйти")
        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            vacancies = db.get_all_vacancies()
            if not vacancies:
                print("Вакансий нет.")
            else:
                for v in vacancies:
                    print(format_vacancy(v))

        elif choice == "2":
            vacancies = db.get_vacancies_with_higher_salary()
            if not vacancies:
                print("Вакансий с зарплатой выше средней нет.")
            else:
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