# HW11 — Менеджер задач: инлайн-формы и Admin actions

Модели приложения `tasks`: **Category**, **Task**, **SubTask** — зарегистрированы в админке (`tasks/admin.py`).

## Что сделано

1. **Инлайн-формы.** В `TaskAdmin` подключён `SubTaskInline` (`TabularInline`, `extra = 1`):
   при создании задачи на той же странице можно сразу создать подзадачу.
2. **Укороченное название.** В списке задач вместо `title` выводится `short_title` —
   первые 10 символов и «...», если название длиннее. `Task.__str__` возвращает полное
   название, поэтому при выборе задачи для подзадачи видно полное название.
3. **Action для подзадач.** `mark_as_done` — действие «Перевести выбранные подзадачи
   в статус Done» в списке подзадач.

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env        # и впишите свой SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Админка: http://127.0.0.1:8000/admin/
