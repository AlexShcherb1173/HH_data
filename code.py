# import os
# from dotenv import load_dotenv
#
# load_dotenv()
#
# print(repr(os.getenv("DB_NAME")))
# print(repr(os.getenv("DB_USER")))
# print(repr(os.getenv("DB_PASSWORD")))


# import os
# import psycopg2
# from dotenv import load_dotenv
#
# load_dotenv()
#
# dbname = os.getenv("DB_NAME").strip()
# user = os.getenv("DB_USER").strip()
# password = os.getenv("DB_PASSWORD").strip()
# host = os.getenv("DB_HOST").strip()
# port_str = os.getenv("DB_PORT").strip()
#
# if not port_str:
#     raise ValueError("Переменная окружения DB_PORT не установлена!")
# port = int(port_str)
# conn = psycopg2.connect(
#     dbname=dbname,
#     user=user,
#     password=password,
#     host=host,
#     port=port
# )
# print("Соединение успешно!")
# conn.close()

import os
from dotenv import load_dotenv

load_dotenv()

for var in ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]:
    value = os.getenv(var)
    print(f"{var!r} = {value!r}")

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

# Получаем переменные окружения
dbname = os.getenv("DB_NAME", "").strip()
user = os.getenv("DB_USER", "").strip()
password = os.getenv("DB_PASSWORD", "").strip()
host = os.getenv("DB_HOST", "").strip()
port_str = os.getenv("DB_PORT", "").strip()

# Проверяем наличие порта
if not port_str:
    raise ValueError("Переменная окружения DB_PORT не установлена!")
port = int(port_str)

# Подключаемся к PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("Соединение успешно!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
finally:
    if 'conn' in locals():
        conn.close()