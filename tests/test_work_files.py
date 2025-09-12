# тесты с использованием pytest и модуля tmp_path для временных файлов, чтобы ничего не сохранять навсегда на диск
# Что делают тесты#
# Проверяют корректную запись и чтение JSON (save_to_json + load_from_json).#
# Проверяют, что файл реально создаётся.#
# Проверяют запись CSV и правильность прочитанных данных.#
# Проверяют случай пустого списка для CSV (только заголовок).
# test_save_json_none — проверяет, что save_to_json корректно обрабатывает None.
# test_load_json_invalid — проверяет ошибку при попытке загрузки невалидного JSON.#
# test_save_csv_empty_fieldnames — проверяет работу save_to_csv, если fieldnames=[].#
# test_save_csv_none_data — проверяет, что при data=None выбрасывается TypeError.
# Используется tmp_path для временных файлов — ничего не остаётся на диске после теста.#
# Проверяются и корректные данные, и граничные случаи (None, пустые списки, пустые fieldnames).#
# Для CSV учтено, что csv.DictReader всегда возвращает строки.#
# Для некорректного JSON ловится json.JSONDecodeError.

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from src.work_files import load_from_json, save_to_csv, save_to_json

# ------------------ JSON ------------------


def test_save_and_load_json(tmp_path: Path) -> None:
    file_path = tmp_path / "data.json"
    data: List[Dict[str, Any]] = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    save_to_json(str(file_path), data)
    loaded = load_from_json(str(file_path))

    assert loaded == data


def test_save_json_empty_list(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.json"
    save_to_json(str(file_path), [])
    loaded = load_from_json(str(file_path))
    assert loaded == []


def test_save_json_none(tmp_path: Path) -> None:
    file_path = tmp_path / "none.json"
    save_to_json(file_path, None)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert content.strip() == "null"


def test_load_json_invalid(tmp_path: Path) -> None:
    file_path = tmp_path / "invalid.json"
    file_path.write_text("invalid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_from_json(file_path)


# ------------------ CSV ------------------


def test_save_and_read_csv(tmp_path: Path) -> None:
    file_path = tmp_path / "data.csv"
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    fieldnames = ["id", "name"]

    save_to_csv(file_path, data, fieldnames)

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # csv.DictReader всегда возвращает значения как строки
        expected = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
        assert rows == expected


def test_save_csv_empty_list(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.csv"
    save_to_csv(file_path, [], ["id", "name"])
    with open(file_path, newline="", encoding="utf-8") as f:
        content = f.read().strip()
        # Только заголовок
        assert content == "id,name"


def test_save_csv_empty_fieldnames(tmp_path: Path) -> None:
    file_path = tmp_path / "empty_fields.csv"
    with pytest.raises(ValueError):
        save_to_csv(file_path, [{"id": 1, "name": "Alice"}], [])


def test_save_csv_none_data(tmp_path: Path) -> None:

    file_path = tmp_path / "none_data.csv"
    with pytest.raises(TypeError):
        save_to_csv(file_path, None, ["id", "name"])
