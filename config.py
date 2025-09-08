from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass

class DBConfig:
    """Конфигурация загрузки .env:"""
    host: str = os.getenv("PG_HOST", "localhost")
    port: int = int(os.getenv("PG_PORT", 5432))
    dbname: str = os.getenv("PG_DB", "hh_db")
    user: str = os.getenv("PG_USER", "hh_user")
    password: str = os.getenv("PG_PASSWORD", "secret")

DB = DBConfig()