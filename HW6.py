import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from pydantic import ValidationError

from schemas.question import (
    CategoryBase,
    CategoryResponse,
    QuestionCreate,
    QuestionResponse,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "quiz.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.ensure_ascii = False  # чтобы русский текст в ответах был читаемым

db = SQLAlchemy(app)
migrations_dir = os.path.join(BASE_DIR, "migrations")
Migrate(app, db, directory=migrations_dir, render_as_batch=True)


# ================== Модели ==================

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    questions = db.relationship("Question", back_populates="category")


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", name="fk_questions_category_id"),
        nullable=True,
    )

    category = db.relationship("Category", back_populates="questions")


# ================== Вспомогательное ==================

def get_json_body():
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Тело запроса должно быть в формате JSON"}), 400)
    return data, None


def validation_error(e: ValidationError):
    return jsonify({"error": "Ошибка валидации", "details": e.errors(include_url=False)}), 422


def not_found(what: str, obj_id: int):
    return jsonify({"error": f"{what} с id={obj_id} не найдена"}), 404


# ================== Категории ==================

@app.post("/categories")
def create_category():
    data, err = get_json_body()
    if err:
        return err
    try:
        payload = CategoryBase.model_validate(data)
    except ValidationError as e:
        return validation_error(e)

    category = Category(name=payload.name)
    db.session.add(category)
    db.session.commit()
    return jsonify(CategoryResponse.model_validate(category).model_dump()), 201


@app.get("/categories")
def list_categories():
    categories = Category.query.order_by(Category.id).all()
    return jsonify([CategoryResponse.model_validate(c).model_dump() for c in categories])


@app.put("/categories/<int:category_id>")
def update_category(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        return not_found("Категория", category_id)

    data, err = get_json_body()
    if err:
        return err
    try:
        payload = CategoryBase.model_validate(data)
    except ValidationError as e:
        return validation_error(e)

    category.name = payload.name
    db.session.commit()
    return jsonify(CategoryResponse.model_validate(category).model_dump())


@app.delete("/categories/<int:category_id>")
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        return not_found("Категория", category_id)

    # Вопросы не удаляем — просто отвязываем их от категории
    for question in category.questions:
        question.category_id = None

    db.session.delete(category)
    db.session.commit()
    return "", 204


# ================== Вопросы ==================

@app.get("/questions")
def list_questions():
    questions = Question.query.order_by(Question.id).all()
    return jsonify([QuestionResponse.model_validate(q).model_dump() for q in questions])


@app.post("/questions")
def create_question():
    data, err = get_json_body()
    if err:
        return err
    try:
        payload = QuestionCreate.model_validate(data)
    except ValidationError as e:
        return validation_error(e)

    if payload.category_id is not None and db.session.get(Category, payload.category_id) is None:
        return not_found("Категория", payload.category_id)

    question = Question(text=payload.text, category_id=payload.category_id)
    db.session.add(question)
    db.session.commit()
    return jsonify(QuestionResponse.model_validate(question).model_dump()), 201


# ================== Запуск ==================

if __name__ == "__main__":
    with app.app_context():
        if not os.path.isdir(migrations_dir):
            init(directory=migrations_dir)
        migrate(directory=migrations_dir, message="auto")
        upgrade(directory=migrations_dir)

    app.run(debug=True, use_reloader=False)
