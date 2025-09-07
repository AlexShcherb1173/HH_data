# pt.ps1
# Скрипт для запуска pytest с параметрами из pytest.ini
# Если нужно, можно добавить свои опции

pytest --cov=src @args

#Здесь @args передаст в pytest все аргументы,
#которые после .\pt.ps1 (например .\pt.ps1 -k test_smartphone).