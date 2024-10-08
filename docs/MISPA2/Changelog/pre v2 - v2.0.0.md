Breaking changes:
- Проект переехал на менеджер пакетов и зависимостей `poetry`
- Центральная сущность приложения `MisApp` была декомпозирована и заменена на `lifespan`
- Все расширения `core` такие как базы данных, кэши, вариайблы, планировщики вынесены в синглтоны `libs`
- В состав файлов проекта включена документация docs, лучше всего открывать через [Obsidian - Sharpen your thinking](https://obsidian.md/)
- Добавлены юнитесты для базовой проверки ендпоинтов
- Для всех ендпоинтов внедрен универсальный json ответ сервера
- Добавлен `Guardian` на замену `Restricted Objects`
- Добавлена поддержка `mongodb`
- В архитектуру внедрен `service/repository` паттерн

core: v2.0.0
- Добавлены категории для модулей (пока в виде простых строк)
- Добавлены зависимости для модулей
- Добавлен вспомогательный метод для модуля для получения информации о нем
- Временно отключена авторизация для ускорения разработки
- Рефактор контекста для Консьюмеров и Джобов
- Добавлен круд
- Правки модели Permissions
- Временно отключен SettingType Enum ввиду ошибки при миграции
- Правки схемы моделей
- Правки зависимостей
- Улучшен процесс инициализации
    - Добавлены пермишены
    - Инкапсулирован модуль лоадер
- Правки в абстрактном классе компоненты модуля
- Добавлена поддержка зависимостей модулей в модуль лоадер
- Правки в функционале нотификаций
- Рефакторинг сервиса редис
- Правки в роутах для круда
- JWT токен не устаревает в дев окружении
- Удален старый код миграций
- Джобы - удален `or_cron_list` - заменен на просто `cron`
- Додано систему керування доступом до об'єктів - [[Guardian]]
- Видалено стару логіку керування доступі до об'єктів - Restricted objects
- Додано файл manifest.json для кожного модуля, основна причина це визначати залежності модулів до їх завантаження.
- Реалізовано паттерн [[Repositories & Services]]
- CRUD сервіси повністю видалено, замінено сервісами з репозиторіями
- Винесено бізнес логіку із ендпоінтів в сервіси
- Додано новий пакет fastapi-pagination для пагінації
- Всі ендпоінти тепер повертають відповідь в однаковому форматі - MisResponse та PageResponse для відповіді з пагінацією
- Додано pytest тести для тестування ендпоінтів
- В таблицю Module  додано enum поле state із можливими значеннями: pre_initialized, initialized, running, stopped, shutdown, error
- Видалено пакет passlib, який використовувався для генерування хешу пароля та його верифікації, замінено пакетом bcrypt
- Додано можливість в /modules/ ендпоінтах виконувати запит не лише по module_id, а і по module_name


dummy: v1.1
- Модуль адаптирован к версии платформы v2.0.0
- Пришел на замену модулю `example`
- Не обладает полезным функционалом но служит практическим справочником и примером как быстро реализовывать стандартные конструкции модулей и работать со встроенным функционалом `core`

binom_companion: v0.5
- Модуль адаптирован к версии платформы v2.0.0
- Переосмыслена концепция работы модуля:
	- Основой является `TrackerInstance` набор данных для подключение и работы с трекером Binom.
	- `ReplacementGroup` набор параметров по которым определяется целевой набор лендингов и офферов.
	- `ProxyDomain` прокси домены для замены в трекере.
	- `ReplacementHistory` подробная история замены доменов.
- Почти все `Settings` перенесены в модели базы данных
- Добавлен консьюмер на событие создание прокси домена для проверки валидности A записи
- Полный рефакторинг моделей:
	- `Proxy` расширен до `ProxyDomain`
	- `Geo` расширен до `ReplacementGroup`
	- `ChangedDomain` расширен до `ReplacementHistory`
	- `LeadRecord` добавлено больше полей.
	- Добавлена модель `TrackerInstance`.
- Рефакторинг схем роутов. Убраны `pydantic_model_creator` и переписаны на классы.
- Добавлен `manifest.json`
- Прописаны scope права на ендпоинты.
- Добавлены миграции базы данных.
- Добавлены репозитории для работы с моделями БД.
- Вся логика работы вынесена в сервисный слой.
- Переписаны роуты для базовых операций CRUD а так же добавлены роуты для проверки подключения к трекеру, проверки работы групп, замены домена.
- Таски:
	- Активные проверки с коэффициентами пока что отключены.
	- Портирована таска для проверки бана по Yandex
	- Таски для замены доменов по крону переписаны для работы с сервисами.
- Утилиты:
	- Удален код работы с гугл таблицами.
	- Остальной код был перенесен в сервисы.
	- Остался код работы с Редис который тоже будет перенесен в сервис (когда будут включены обратно активные проверки)
- Удален код и модели для работы с socks прокси. Этот функционал будет имплементирован в модуле `proxy_registry`

proxy_registry: v0.2
- Модуль адаптирован к версии платформы v2.0.0
- Пришел на замену модулю `proxy`
- Является модулем-библиотекой: содержит регистр всех socks5 прокси которые будут использоваться другими модулями, имеет методы для работы с ними например для проверки работоспособности прокси, автозамена IP по таймеру.