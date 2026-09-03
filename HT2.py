from pydantic import BaseModel, field_validator, model_validator, EmailStr
from pydantic import ValidationError
import json


class Address(BaseModel):
    city: str
    street: str
    house_number: int

    @field_validator("city")
    def validate_city(cls, v):
        if len(v) < 2:
            raise ValueError("City must be at least 2 characters.")
        return v

    @field_validator("street")
    def validate_street(cls, v):
        if len(v) < 3:
            raise ValueError("Street must be at least 3 characters.")
        return v

    @field_validator("house_number")
    def validate_house_number(cls, v):
        if v <= 0:
            raise ValueError("House number must be positive.")
        return v


class User(BaseModel):
    name: str
    age: int
    email: EmailStr
    is_employed: bool
    address: Address

    @field_validator("name")
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters.")
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError("Name must contain only letters.")
        return v

    @field_validator("age")
    def validate_age(cls, v):
        if not 0 <= v <= 120:
            raise ValueError("Age must be between 0 and 120.")
        return v

    @model_validator(mode="after")
    def validate_employment(self):
        if self.is_employed and not (18 <= self.age <= 65):
            raise ValueError("Employed users must be between 18 and 65 years old.")
        return self


def register_user(json_input: str):
    try:
        data = json.loads(json_input)
        user = User(**data)
        print("Регистрация успешна!")
        return user.model_dump_json(indent=4)
    except ValidationError as e:
        print("Ошибка валидации:")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")
        return None


# Тест 1: Успешная регистрация
json1 = (
    '{"name": "Alice Smith", "age": 30, "email": "alice@example.com",'
    '"is_employed": true, "address": {"city": "Berlin",'
    '"street": "Main Street", "house_number": 5}}'
)

# Тест 2: Занят, но возраст 70 - ошибка
json2 = (
    '{"name": "John Doe", "age": 70, "email": "john@example.com",'
    '"is_employed": true, "address": {"city": "New York",'
    '"street": "5th Avenue", "house_number": 123}}'
)

# Тест 3: Не занят, возраст 70 - успешно
json3 = (
    '{"name": "Bob Brown", "age": 70, "email": "bob@example.com",'
    '"is_employed": false, "address": {"city": "Paris",'
    '"street": "Rue de Rivoli", "house_number": 10}}'
)

# Тест 4: Некорректное имя - ошибка
json4 = (
    '{"name": "J", "age": 25, "email": "j@example.com",'
    '"is_employed": true, "address": {"city": "London",'
    '"street": "Baker Street", "house_number": 221}}'
)

for i, json_input in enumerate([json1, json2, json3, json4], 1):
    print(f"\n--- Тест {i} ---")
    result = register_user(json_input)
    if result:
        print(result)