from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.permissions import get_board_or_404, require_board_access

router = APIRouter(tags=["cards"])


def _get_list_or_404(db: Session, list_id: int) -> models.TaskList:
    lst = db.get(models.TaskList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    return lst


def _get_card_or_404(db: Session, card_id: int) -> models.Card:
    card = db.get(models.Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


def _card_out(card: models.Card) -> schemas.CardOut:
    return schemas.CardOut(
        id=card.id,
        list_id=card.list_id,
        title=card.title,
        description=card.description,
        position=card.position,
        priority=card.priority,
        due_date=card.due_date,
        created_by=card.created_by,
        created_at=card.created_at,
        labels=[schemas.LabelOut.model_validate(l) for l in card.labels],
        comment_count=len(card.comments),
        attachment_count=len(card.attachments),
    )


@router.post("/lists/{list_id}/cards", response_model=schemas.CardOut, status_code=status.HTTP_201_CREATED)
def create_card(
    list_id: int,
    payload: schemas.CardCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    lst = _get_list_or_404(db, list_id)
    board = get_board_or_404(db, lst.board_id)
    require_board_access(db, board, user)

    max_pos = max([c.position for c in lst.cards], default=-1)
    card = models.Card(
        list_id=list_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        position=max_pos + 1,
        created_by=user.id,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return _card_out(card)


@router.get("/cards/{card_id}", response_model=schemas.CardOut)
def get_card(card_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)
    return _card_out(card)


@router.patch("/cards/{card_id}", response_model=schemas.CardOut)
def update_card(
    card_id: int,
    payload: schemas.CardUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)

    data = payload.model_dump(exclude_unset=True)
    if "list_id" in data and data["list_id"] is not None:
        target_list = _get_list_or_404(db, data["list_id"])
        if target_list.board_id != board.id:
            raise HTTPException(status_code=400, detail="Cannot move card to a list on another board")
        card.list_id = data["list_id"]
    for field in ("title", "description", "priority", "due_date", "position"):
        if field in data and data[field] is not None:
            setattr(card, field, data[field])

    db.commit()
    db.refresh(card)
    return _card_out(card)


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)
    db.delete(card)
    db.commit()


@router.post("/cards/{card_id}/labels/{label_id}", response_model=schemas.CardOut)
def add_label_to_card(
    card_id: int, label_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)

    label = db.get(models.Label, label_id)
    if not label or label.board_id != board.id:
        raise HTTPException(status_code=404, detail="Label not found on this board")
    if label not in card.labels:
        card.labels.append(label)
        db.commit()
        db.refresh(card)
    return _card_out(card)


@router.delete("/cards/{card_id}/labels/{label_id}", response_model=schemas.CardOut)
def remove_label_from_card(
    card_id: int, label_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)

    label = db.get(models.Label, label_id)
    if label and label in card.labels:
        card.labels.remove(label)
        db.commit()
        db.refresh(card)
    return _card_out(card)


@router.post("/cards/{card_id}/comments", response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    card_id: int,
    payload: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)

    comment = models.Comment(card_id=card_id, user_id=user.id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return schemas.CommentOut(
        id=comment.id,
        card_id=comment.card_id,
        user_id=comment.user_id,
        username=user.username,
        content=comment.content,
        created_at=comment.created_at,
    )


@router.get("/cards/{card_id}/comments", response_model=list[schemas.CommentOut])
def list_comments(card_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)
    return [
        schemas.CommentOut(
            id=c.id, card_id=c.card_id, user_id=c.user_id, username=c.user.username, content=c.content,
            created_at=c.created_at,
        )
        for c in card.comments
    ]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    comment = db.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    db.delete(comment)
    db.commit()
