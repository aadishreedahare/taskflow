from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(tags=["search"])


@router.get("/search/cards", response_model=list[schemas.CardOut])
def search_cards(
    q: str | None = Query(None, description="Text to search in title/description"),
    priority: models.Priority | None = None,
    board_id: int | None = None,
    label_id: int | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    """
    Search/filter cards across every board the current user can access.
    Combines a text search with optional priority / board / label filters.
    """
    accessible_board_ids = [b.id for b in user.owned_boards] + [m.board_id for m in user.memberships]

    query = (
        db.query(models.Card)
        .join(models.TaskList, models.Card.list_id == models.TaskList.id)
        .filter(models.TaskList.board_id.in_(accessible_board_ids))
    )

    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Card.title.ilike(like), models.Card.description.ilike(like)))
    if priority:
        query = query.filter(models.Card.priority == priority)
    if board_id:
        query = query.filter(models.TaskList.board_id == board_id)
    if label_id:
        query = query.join(models.CardLabel, models.CardLabel.card_id == models.Card.id).filter(
            models.CardLabel.label_id == label_id
        )

    cards = query.distinct().order_by(models.Card.created_at.desc()).limit(100).all()
    return [
        schemas.CardOut(
            id=c.id,
            list_id=c.list_id,
            title=c.title,
            description=c.description,
            position=c.position,
            priority=c.priority,
            due_date=c.due_date,
            created_by=c.created_by,
            created_at=c.created_at,
            labels=[schemas.LabelOut.model_validate(l) for l in c.labels],
            comment_count=len(c.comments),
            attachment_count=len(c.attachments),
        )
        for c in cards
    ]
