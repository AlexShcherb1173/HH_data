import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

class DBConfig:
    """Конфигурация для подключения к PostgreSQL."""
    name: str = os.getenv("DB_NAME", "hh_db").strip()
    user: str = os.getenv("DB_USER", "postgres").strip()
    password: str = os.getenv("DB_PASSWORD", "12345").strip()
    host: str = os.getenv("DB_HOST", "localhost").strip()
    port: int = int(os.getenv("DB_PORT", 5432).strip())