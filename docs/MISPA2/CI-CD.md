## [WIP] План имплементации пайплайна

## Source
Реализовать проверку Linting. Проверка выполняется в момент Merge Request из дев ветки в Main.
Без пройденолой проверки не выполнять апрув реквеста. <br>

Реализовать Branch Protection. Ветка Main не доступна для изменения напрямую, только через review мекрдж реквеста.

## Build

На этом этапе происходит сборка `docker` образа проекта и запуск `unit` тестов. <br>
В идеале нужно добиться 80-90% покрытия кода такими тестами.

## Test

На этом этапе запускаются `integration` тесты. Набор сценариев при котором мы проверяем взаимодействие юзера с платформой.

## Release

На этом этапе собранный образ можно разворачивать на `stage` и `production`
