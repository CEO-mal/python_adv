# HW13 — Менеджер задач: сериализаторы и классы представлений

Модели приложения `tasks`: **Category**, **Task**, **SubTask**.

## Что сделано (`tasks/serializers.py`, `tasks/views.py`, `tasks/urls.py`)

1. **SubTaskCreateSerializer** — поле `created_at` переопределено как `read_only`.
2. **CategoryCreateSerializer** — в `create` и `update` проверяется уникальность названия
   (без учёта регистра); при совпадении — ошибка валидации 400.
3. **TaskDetailSerializer** — вложенный `SubTaskSerializer(many=True)`: задача отдаётся со всеми подзадачами.
4. **TaskCreateSerializer** — `validate_deadline`: дедлайн не может быть в прошлом.
5. **SubTaskListCreateView** и **SubTaskDetailUpdateDeleteView** на `APIView`.

## Эндпоинты

| Метод                     | URL                       | Что делает                          |
|---------------------------|---------------------------|-------------------------------------|
| GET, POST                 | `/api/subtasks/`          | список / создание подзадач          |
| GET, PUT, PATCH, DELETE   | `/api/subtasks/<id>/`     | подзадача: получить / обновить / удалить |
| GET, POST                 | `/api/categories/`        | список / создание категорий         |
| GET, PUT, PATCH, DELETE   | `/api/categories/<id>/`   | категория                           |
| POST                      | `/api/tasks/create/`      | создание задачи                     |
| GET                       | `/api/tasks/`             | список задач                        |
| GET                       | `/api/tasks/<id>/`        | задача со всеми подзадачами         |
| GET                       | `/api/tasks/stats/`       | статистика                          |

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env        # и впишите свой SECRET_KEY
python manage.py migrate
python manage.py runserver
```
