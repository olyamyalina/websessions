# Практическое задание №1, вариант 15

Прототип управляет данными `Account`, `Message` и `Feedback` в памяти,
предоставляет 13 процедур через собственный двоичный RPC поверх TCP.
Корректность RPC проверяется model-based testing на базе Hypothesis.

Данные намеренно не сохраняются на диск. Единственный создаваемый сервером
файл - журнал запросов `journal.log`.

## Структура проекта

- `src/model.py` - исходная функциональная модель и интерактивный REPL;
- `src/protocol.py` - кодирование и чтение двоичных пакетов;
- `src/server.py` - многопоточный TCP RPC-сервер и журналирование;
- `src/client.py` - RPC-клиент с 13 одноименными методами;
- `src/demo_rpc.py` - демонстрация всех процедур и обработки ошибки;
- `tests/test_rpc_state_machine.py` - MBT-тест всех 13 RPC-методов;
- `requirements-dev.txt` - зависимости тестирования;
- `pyproject.toml` - настройки pytest, coverage и Ruff;
- `run.bat`, `run.sh` - единая точка запуска.

## Модель данных и функции

Записи представлены кортежами в порядке полей ER-диаграммы:

- `Account = (uid, timestamp, ip)`;
- `Message = (uid, timestamp, argument, account, completed)`;
- `Feedback = (uid, timestamp, result, status, failure, message)`.

Для каждой сущности реализованы `create_*`, `get_all_*`, `get_*_by_uid` и
`edit_*`. Тринадцатая функция `get_data_sample` выбирает аккаунты, созданные
или измененные за последние восемь минут, выполняет левое внешнее соединение
с `Message` по `Account.uid = Message.account` и возвращает проекцию
`(Account.ip, Message.argument)`. При отсутствии сообщения аргумент равен
`None`.

Первый этап сохраняет функциональную реализацию с глобальными списками из
исходного решения. Единственное смысловое изменение - именованная константа
`SAMPLE_WINDOW_SECONDS` вместо литерала `8 * 60`. Потокобезопасность добавлена
на уровне RPC-сервера, поэтому функции первого этапа не пришлось переделывать
в класс.

Редактирование обновляет `timestamp`. Внешние ключи проверяются: нельзя
создать `Message` без существующего `Account` и `Feedback` без `Message`.

## Формат RPC

Запрос и ответ имеют одинаковое обрамление:

| Смещение | Размер | Значение |
|---:|---:|---|
| 0 | 3 байта | размер JSON-тела, little-endian |
| 3 | 1 байт | код операции |
| 4 | переменный | JSON в UTF-8 |

Размер обозначает только JSON-тело, без четырех байтов заголовка. Коды от 1
до 13 соответствуют порядку функций в `src/client.py`. Тело запроса - объект
с именованными аргументами. Успешный ответ имеет вид
`{"ok": true, "result": ...}`, ошибочный - поля `ok`, `error`, `message`.

Настройки по умолчанию: адрес `127.0.0.1`, порт `9000`, тайм-аут клиента 5
секунд, журнал `journal.log`. Сервер поддерживает параметры `--host`, `--port`
и `--journal`.

## Установка и запуск

Требуется Python 3.10 или новее. Рабочий код использует стандартную библиотеку
Python. Для третьего этапа установите тестовые зависимости:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
```

Запуск REPL модели:

```bat
run.bat model
```

Запуск сервера в первом терминале и демонстрации во втором:

```bat
run.bat server
run.bat demo
```

Пример отдельного запуска с настройками:

```bash
python -m src.server --host 127.0.0.1 --port 9001 --journal logs/rpc.log
```

## Примеры использования

Прямое обращение к модели:

```python
from src.model import create_account, create_message, get_data_sample

account = create_account("127.0.0.1")
create_message("ping", account[0], 0)
print(get_data_sample())
```

Удаленный вызов:

```python
from src.client import RPCClient

client = RPCClient("127.0.0.1", 9000)
account = client.create_account("127.0.0.1")
message = client.create_message("ping", account[0], 0)
print(client.get_message_by_uid(message[0]))
```

## Этап 3

`RuleBasedStateMachine` из Hypothesis генерирует последовательности операций
над настоящим TCP RPC-сервером. Параллельно тест хранит упрощенную модель в
словарях и после каждого шага сравнивает все три отношения и результат
`get_data_sample`. Инициализация state machine вызывает все 13 RPC-методов.

Запуск MBT и формирование отчета о покрытии ветвей:

```bat
run.bat test
```

Эквивалентные команды:

```bat
coverage run --branch -m pytest
coverage report -m
coverage html
```

Текстовый отчет выводится в терминал. HTML-отчет создается в
`htmlcov/index.html`; отчеты и служебные файлы исключены через `.gitignore`.

## Оформление истории Git

Этапы следует фиксировать отдельными Conventional/Scoped Commits:

```text
feat(model): implement in-memory data access layer
feat(rpc): add TCP remote procedure calls
test(mbt): cover RPC methods with Hypothesis state machine
```

В репозиторий не добавляются `journal.log`, кэш Python, окружение, отчет
покрытия и настройки редакторов - они перечислены в `.gitignore`.
