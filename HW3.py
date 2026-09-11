from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, relationship

# Задача 1: Движок для SQLite в памяти
engine = create_engine("sqlite:///:memory:", echo=True)

# Задача 2: Сессия
session = Session(engine)

# Base класс
class Base(DeclarativeBase):
    pass

# Задача 4: Модель Category
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(255))

    # Связь с Product
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name})"

# Задача 3 + 5: Модель Product со связью
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Numeric(10, 2))
    in_stock = Column(Boolean)

    # Задача 5: Связь с Category
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price})"

# Создаём таблицы
Base.metadata.create_all(engine)

# Проверка
category1 = Category(name="Electronics", description="Electronic devices")
product1 = Product(name="Laptop", price=999.99, in_stock=True, category=category1)
product2 = Product(name="Phone", price=499.99, in_stock=False, category=category1)

session.add_all([category1, product1, product2])
session.commit()

# Запрос
products = session.query(Product).all()
for p in products:
    print(p, "| Category:", p.category.name)

session.close()