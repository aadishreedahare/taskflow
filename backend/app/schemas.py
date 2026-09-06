from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import BoardRole, Priority


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    username: str
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Labels ----------

class LabelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    color: str = "#3b82f6"


class LabelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    board_id: int
    name: str
    color: str


# ---------- Comments ----------

class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    card_id: int
    user_id: int
    username: str | None = None
    content: str
    created_at: datetime


# ---------- Attachments ----------

class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    card_id: int
    filename: str
    content_type: str | None
    size_bytes: int
    uploaded_by: int
    created_at: datetime


# ---------- Cards ----------

class CardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: Priority = Priority.medium
    due_date: date | None = None


class CardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    due_date: date | None = None
    list_id: int | None = None
    position: int | None = None


class CardReorder(BaseModel):
    list_id: int
    position: int


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    list_id: int
    title: str
    description: str | None
    position: int
    priority: Priority
    due_date: date | None
    created_by: int
    created_at: datetime
    labels: list[LabelOut] = []
    comment_count: int = 0
    attachment_count: int = 0


# ---------- Lists ----------

class ListCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ListUpdate(BaseModel):
    title: str | None = None
    position: int | None = None


class ListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    board_id: int
    title: str
    position: int
    cards: list[CardOut] = []


# ---------- Board members ----------

class MemberInvite(BaseModel):
    email: EmailStr


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    username: str
    email: EmailStr
    role: BoardRole


# ---------- Boards ----------

class BoardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class BoardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    owner_id: int
    created_at: datetime


class BoardDetailOut(BoardOut):
    lists: list[ListOut] = []
    labels: list[LabelOut] = []
    members: list[MemberOut] = []


# ---------- Admin ----------

class AdminStats(BaseModel):
    total_users: int
    total_boards: int
    total_cards: int
    total_lists: int
    cards_by_priority: dict[str, int]
