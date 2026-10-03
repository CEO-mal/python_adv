# HW10 — Менеджер задач: ORM-запросы (CRUD)

Модели приложения `tasks`: **Category**, **Task**, **SubTask** — зарегистрированы в админке.

```bash
pip install -r requirements.txt
cp .env.example .env        # и впишите свой SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Админка: http://127.0.0.1:8000/admin/

ORM-запросы: `orm_queries.py`

```bash
python manage.py shell < orm_queries.py
```
