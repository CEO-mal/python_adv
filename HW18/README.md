# HW15 — Менеджер задач: Generic Views, фильтрация, поиск и сортировка

Модели приложения `tasks`: **Category**, **Task**, **SubTask**.
Код: `tasks/views.py`, `tasks/filters.py`, `tasks/urls.py`.

## Эндпоинты (полный CRUD)

| Метод                   | URL                    | Представление                       |
|-------------------------|------------------------|-------------------------------------|
| GET, POST               | `/api/tasks/`          | `TaskListCreateView` (ListCreateAPIView) |
| GET, PUT, PATCH, DELETE | `/api/tasks/<id>/`     | `TaskRetrieveUpdateDestroyView` (RetrieveUpdateDestroyAPIView) |
| GET                     | `/api/tasks/stats/`    | `TaskStatsView` — статистика, без изменений |
| GET, POST               | `/api/subtasks/`       | `SubTaskListCreateView` (ListCreateAPIView) |
| GET, PUT, PATCH, DELETE | `/api/subtasks/<id>/`  | `SubTaskRetrieveUpdateDestroyView` (RetrieveUpdateDestroyAPIView) |

## Фильтрация, поиск, сортировка (для задач и подзадач)

| Что            | Параметр                                  | Пример                                  |
|----------------|-------------------------------------------|-----------------------------------------|
| статус         | `status`                                  | `?status=done`                          |
| дедлайн        | `deadline` (точно)                        | `?deadline=2026-11-10T09:00:00%2B01:00` |
| дедлайн в день | `deadline_date`                           | `?deadline_date=2026-11-03`             |
| период         | `deadline_after`, `deadline_before`       | `?deadline_after=2026-11-05`            |
| поиск          | `search` — по `title` и `description`     | `?search=API`                           |
| сортировка     | `ordering` — по `created_at`              | `?ordering=created_at`, `?ordering=-created_at` |

Параметры можно сочетать: `/api/subtasks/?status=done&search=API&ordering=created_at`.
По умолчанию — сначала новые. Подзадачи выводятся по 5 на странице (`?page=2`).
Дополнительно: задачи — `?weekday=вторник`, подзадачи — `?task_title=релиз`.

В браузере (DRF) фильтры доступны по кнопке **Filters**.

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env        # и впишите свой SECRET_KEY
python manage.py migrate
python manage.py runserver
```
