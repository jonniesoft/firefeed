from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr, Field

# Определяем типовой параметр для Generic
T = TypeVar("T")


# Модель для представления перевода на конкретный язык
class LanguageTranslation(BaseModel):
    title: str | None = None
    content: str | None = None


# Модель для представления новости в API
class RSSItem(BaseModel):
    news_id: str
    original_title: str
    original_content: str
    original_language: str
    image_url: str | None = None
    category: str | None = None
    source: str | None = None  # Имя источника новости
    source_url: str | None = None
    published_at: str | None = None  # ISO формат даты-времени
    translations: dict[str, LanguageTranslation] | None = None

    class Config:
        from_attributes = True


class CategoryItem(BaseModel):
    id: int
    name: str


class SourceItem(BaseModel):
    id: int
    name: str
    description: str | None = None


class LanguageItem(BaseModel):
    language: str


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    results: list[T]


# Модель для ответа с ошибкой (опционально, но полезно)
class HTTPError(BaseModel):
    detail: str


# --- Модели для пользователей ---


class UserBase(BaseModel):
    email: EmailStr
    language: str = "en"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    language: str | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: int | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# --- Модели для верификации пользователей ---


class EmailVerificationRequest(BaseModel):
    """Модель для запроса верификации email пользователя."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class SuccessResponse(BaseModel):
    """Модель для ответа об успешной операции."""

    message: str


# --- Модели для пользовательских RSS-лент ---


class UserRSSFeedBase(BaseModel):
    url: str
    name: str | None = None
    category_id: int | None = None
    language: str = "en"


class UserRSSFeedCreate(UserRSSFeedBase):
    pass


class UserRSSFeedUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    is_active: bool | None = None


class UserRSSFeedResponse(UserRSSFeedBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserCategoriesUpdate(BaseModel):
    category_ids: set[int]


class UserCategoriesResponse(BaseModel):
    category_ids: list[int]


# --- Модели для привязки Telegram ---


class TelegramLinkResponse(BaseModel):
    link_code: str
    instructions: str


class TelegramLinkStatusResponse(BaseModel):
    is_linked: bool
    telegram_id: int | None = None
    linked_at: str | None = None
