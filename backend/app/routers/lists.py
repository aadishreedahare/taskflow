from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.permissions import get_board_or_404, require_board_access

router = APIRouter(tags=["lists"])


def _get_list_or_404(db: Session, list_id: int) -> models.TaskList:
    lst = db.get(models.TaskList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    return lst


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


@router.post("/boards/{board_id}/lists", response_model=schemas.ListOut, status_code=status.HTTP_201_CREATED)
def create_list(
    board_id: int,
    payload: schemas.ListCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    board = get_board_or_404(db, board_id)
    require_board_access(db, board, user)
    max_pos = max([l.position for l in board.lists], default=-1)
    lst = models.TaskList(board_id=board_id, title=payload.title, position=max_pos + 1)
    db.add(lst)
    db.commit()
    db.refresh(lst)
    return schemas.ListOut(id=lst.id, board_id=lst.board_id, title=lst.title, position=lst.position, cards=[])


@router.patch("/lists/{list_id}", response_model=schemas.ListOut)
def update_list(
    list_id: int,
    payload: schemas.ListUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    lst = _get_list_or_404(db, list_id)
    board = get_board_or_404(db, lst.board_id)
    require_board_access(db, board, user)

    if payload.title is not None:
        lst.title = payload.title
    if payload.position is not None:
        lst.position = payload.position
    db.commit()
    db.refresh(lst)
    return schemas.ListOut(
        id=lst.id,
        board_id=lst.board_id,
        title=lst.title,
        position=lst.position,
        cards=[_card_out(c) for c in lst.cards],
    )


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(list_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    lst = _get_list_or_404(db, list_id)
    board = get_board_or_404(db, lst.board_id)
    require_board_access(db, board, user)
    db.delete(lst)
    db.commit()
