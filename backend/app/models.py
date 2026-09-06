import enum
from datetime import datetime, date

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Date,
    Text,
    Boolean,
    Enum,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BoardRole(str, enum.Enum):
    owner = "owner"
    member = "member"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owned_boards: Mapped[list["Board"]] = relationship(back_populates="owner")
    memberships: Mapped[list["BoardMember"]] = relationship(back_populates="user")


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="owned_boards")
    members: Mapped[list["BoardMember"]] = relationship(back_populates="board", cascade="all, delete-orphan")
    lists: Mapped[list["TaskList"]] = relationship(
        back_populates="board", cascade="all, delete-orphan", order_by="TaskList.position"
    )
    labels: Mapped[list["Label"]] = relationship(back_populates="board", cascade="all, delete-orphan")


class BoardMember(Base):
    __tablename__ = "board_members"
    __table_args__ = (UniqueConstraint("board_id", "user_id", name="uq_board_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[BoardRole] = mapped_column(Enum(BoardRole), default=BoardRole.member)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    board: Mapped["Board"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")


class TaskList(Base):
    """A column on a board (e.g. 'To Do', 'In Progress', 'Done')."""

    __tablename__ = "task_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    title: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    board: Mapped["Board"] = relationship(back_populates="lists")
    cards: Mapped[list["Card"]] = relationship(
        back_populates="task_list", cascade="all, delete-orphan", order_by="Card.position"
    )


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    list_id: Mapped[int] = mapped_column(ForeignKey("task_lists.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.medium)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task_list: Mapped["TaskList"] = relationship(back_populates="cards")
    comments: Mapped[list["Comment"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    labels: Mapped[list["Label"]] = relationship(secondary="card_labels", back_populates="cards")


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    name: Mapped[str] = mapped_column(String(64))
    color: Mapped[str] = mapped_column(String(16), default="#3b82f6")

    board: Mapped["Board"] = relationship(back_populates="labels")
    cards: Mapped[list["Card"]] = relationship(secondary="card_labels", back_populates="labels")


class CardLabel(Base):
    __tablename__ = "card_labels"

    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), primary_key=True)
    label_id: Mapped[int] = mapped_column(ForeignKey("labels.id"), primary_key=True)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    card: Mapped["Card"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship()


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    filename: Mapped[str] = mapped_column(String(255))
    filepath: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    card: Mapped["Card"] = relationship(back_populates="attachments")
