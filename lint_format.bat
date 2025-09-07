@echo off
REM ---------- Настройка ----------
REM Папки или файлы для проверки
set FILES=src tests

REM ---------- Форматирование ----------
echo Running black...
black %FILES%

echo Running isort...
isort %FILES%

REM ---------- Статический анализ ----------
echo Running flake8...
flake8 %FILES%

echo Running mypy...
mypy %FILES%

echo Done.
pause