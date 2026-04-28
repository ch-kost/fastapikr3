## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn task_6_1.main:app --reload
uvicorn task_6_2.main:app --reload
uvicorn task_6_3.main:app --reload
uvicorn task_6_4.main:app --reload
uvicorn task_6_5.main:app --reload
uvicorn task_7_1.main:app --reload
```

Для заданий с SQLite сначала создайте таблицы:

```bash
python task_8_1/create_db.py
uvicorn task_8_1.main:app --reload

python task_8_2/create_db.py
uvicorn task_8_2.main:app --reload
```

## Проверка 6.1

```bash
curl -u admin:secret http://127.0.0.1:8000/login
curl -u admin:wrong http://127.0.0.1:8000/login
```

## Проверка 6.2

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"user1\",\"password\":\"correctpass\"}" http://127.0.0.1:8000/register
curl -u user1:correctpass http://127.0.0.1:8000/login
curl -u user1:wrongpass http://127.0.0.1:8000/login
```

## Проверка 6.3

```bash
curl -u admin:admin http://127.0.0.1:8000/docs
curl http://127.0.0.1:8000/docs
```

Для PROD:

```bash
set MODE=PROD
uvicorn task_6_3.main:app --reload
curl http://127.0.0.1:8000/docs
```

## Проверка 6.4

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"john_doe\",\"password\":\"securepassword123\"}" http://127.0.0.1:8000/login
curl -H "Authorization: Bearer TOKEN" http://127.0.0.1:8000/protected_resource
```

## Проверка 6.5

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}" http://127.0.0.1:8000/register
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}" http://127.0.0.1:8000/login
curl -H "Authorization: Bearer TOKEN" http://127.0.0.1:8000/protected_resource
```

## Проверка 7.1

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin1\",\"password\":\"12345\",\"role\":\"admin\"}" http://127.0.0.1:8000/register
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin1\",\"password\":\"12345\"}" http://127.0.0.1:8000/login
curl -H "Authorization: Bearer TOKEN" http://127.0.0.1:8000/admin/resource
```

## Проверка 8.1

```bash
curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" -d "{\"username\":\"test_user\",\"password\":\"12345\"}"
```

## Проверка 8.2

```bash
curl -X POST http://127.0.0.1:8000/todos -H "Content-Type: application/json" -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\"}"
curl http://127.0.0.1:8000/todos/1
curl -X PUT http://127.0.0.1:8000/todos/1 -H "Content-Type: application/json" -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread and cheese\",\"completed\":true}"
curl -X DELETE http://127.0.0.1:8000/todos/1
```
