import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "quiz.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrations_dir = os.path.join(BASE_DIR, "migrations")
Migrate(app, db, directory=migrations_dir, render_as_batch=True)


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


if __name__ == "__main__":
    with app.app_context():
        if not os.path.isdir(migrations_dir):
            init(directory=migrations_dir)                              # flask db init
        migrate(directory=migrations_dir, message="add categories")     # flask db migrate
        upgrade(directory=migrations_dir)                               # flask db upgrade
    print("Миграция выполнена")