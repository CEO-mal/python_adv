from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Категории ----------

class CategoryBase(BaseModel):
    """Данные категории, которые присылает клиент (POST / PUT)."""
    name: str = Field(min_length=1, max_length=100)


class CategoryResponse(CategoryBase):
    """Категория в ответе API."""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------- Вопросы ----------

class QuestionCreate(BaseModel):
    """Данные для создания вопроса. Категория указывается по id (необязательно)."""
    text: str = Field(min_length=1, max_length=255)
    category_id: Optional[int] = None


class QuestionResponse(BaseModel):
    """Вопрос в ответе API вместе с информацией о категории."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    category: Optional[CategoryResponse] = None