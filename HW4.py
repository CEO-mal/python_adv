from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Session, relationship

engine = create_engine("sqlite:///:memory:")
session = Session(engine)

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(255))
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Numeric(10, 2))
    in_stock = Column(Boolean)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

Base.metadata.create_all(engine)

# Задача 1: Наполнение данными
electronics = Category(name="Электроника", description="Гаджеты и устройства.")
books = Category(name="Книги", description="Печатные книги и электронные книги.")
clothes = Category(name="Одежда", description="Одежда для мужчин и женщин.")

session.add_all([electronics, books, clothes])
session.flush()

products = [
    Product(name="Смартфон", price=299.99, in_stock=True, category=electronics),
    Product(name="Ноутбук", price=499.99, in_stock=True, category=electronics),
    Product(name="Научно-фантастический роман", price=15.99, in_stock=True, category=books),
    Product(name="Джинсы", price=40.50, in_stock=True, category=clothes),
    Product(name="Футболка", price=20.00, in_stock=True, category=clothes),
]
session.add_all(products)
session.commit()

# Задача 2: Чтение данных
print("=== Категории и продукты ===")
categories = session.query(Category).all()
for cat in categories:
    print(f"\nКатегория: {cat.name}")
    for p in cat.products:
        print(f"  - {p.name}: {p.price}")

# Задача 3: Обновление данных
smartphone = session.query(Product).filter(Product.name == "Смартфон").first()
smartphone.price = 349.99
session.commit()
print(f"\n=== Обновлена цена смартфона: {smartphone.price} ===")

# Задача 4: Агрегация
print("\n=== Количество продуктов по категориям ===")
result = session.query(
    Category.name,
    func.count(Product.id).label("total")
).join(Product).group_by(Category.id).all()

for name, total in result:
    print(f"{name}: {total} продуктов")

# Задача 5: Категории с более чем 1 продуктом
print("\n=== Категории с более чем 1 продуктом ===")
result = session.query(
    Category.name,
    func.count(Product.id).label("total")
).join(Product).group_by(Category.id).having(func.count(Product.id) > 1).all()

for name, total in result:
    print(f"{name}: {total} продуктов")

session.close()