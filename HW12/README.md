# HW12 — Менеджер задач: API на Django REST Framework

Модели приложения `tasks`: **Category**, **Task**, **SubTask**.

## Эндпоинты

| Метод | URL                   | Что делает                                             |
|-------|-----------------------|--------------------------------------------------------|
| POST  | `/api/tasks/create/`  | создать задачу (title, description, status, deadline)  |
| GET   | `/api/tasks/`         | список задач                                           |
| GET   | `/api/tasks/<id>/`    | задача по ID (404, если такой нет)                     |
| GET   | `/api/tasks/stats/`   | статистика: всего, по статусам, просроченные           |

Код: `tasks/serializers.py`, `tasks/views.py`, `tasks/urls.py`, подключение — `config/urls.py`.

Просроченная задача — дедлайн уже прошёл, а статус не `done`.

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env        # и впишите свой SECRET_KEY
python manage.py migrate
python manage.py runserver
```

## Проверка

```bash
curl -X POST http://127.0.0.1:8000/api/tasks/create/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Подключить DRF", "description": "Эндпоинты для задач", "status": "new", "deadline": "2026-12-31T18:00:00+01:00"}'
curl http://127.0.0.1:8000/api/tasks/
curl http://127.0.0.1:8000/api/tasks/1/
curl http://127.0.0.1:8000/api/tasks/stats/
```
