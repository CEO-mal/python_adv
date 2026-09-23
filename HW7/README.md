# Django project

```bash
pip install -r requirements.txt
cp .env.example .env   # и впишите свой SECRET_KEY
python manage.py migrate
python manage.py runserver
```

Страница: http://127.0.0.1:8000/hello/ → **Hello, Nadiya**

База данных выбирается переменной `MYSQL` в `.env`: `False` — SQLite, `True` — MySQL (параметры `MYSQL_*`).
