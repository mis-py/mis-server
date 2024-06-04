Для того чтобы сделать себе локальное окружение для разработки можно сделать следующее:
1. Добавить файл с названием: *local*.env в каталог `envs`
Пример файла: `user_local.env` или `my_local_1.env`
2. Добавить в конфигурацию запуска в IDE переменную ENVIRONMENT=<envfile>, где envfile мы создали в 1 пункте но без расширения .env
Пример переменной: `ENVIRONMENT=user_local` или `ENVIRONMENT=my_local_1`
3. При запуске проекта в IDE все настройки будут взяты из этого файла, а отсутствующие взяты по умолчанию из `config.py`