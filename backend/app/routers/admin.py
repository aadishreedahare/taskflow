from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[schemas.UserOut])
def list_all_users(db: Session = Depends(get_db), _: models.User = Depends(auth.get_current_admin)):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.get("/boards", response_model=list[schemas.BoardOut])
def list_all_boards(db: Session = Depends(get_db), _: models.User = Depends(auth.get_current_admin)):
    return db.query(models.Board).order_by(models.Board.created_at.desc()).all()


@router.get("/stats", response_model=schemas.AdminStats)
def get_stats(db: Session = Depends(get_db), _: models.User = Depends(auth.get_current_admin)):
    total_users = db.query(func.count(models.User.id)).scalar()
    total_boards = db.query(func.count(models.Board.id)).scalar()
    total_cards = db.query(func.count(models.Card.id)).scalar()
    total_lists = db.query(func.count(models.TaskList.id)).scalar()

    rows = db.query(models.Card.priority, func.count(models.Card.id)).group_by(models.Card.priority).all()
    cards_by_priority = {p.value: count for p, count in rows}
    for p in models.Priority:
        cards_by_priority.setdefault(p.value, 0)

    return schemas.AdminStats(
        total_users=total_users,
        total_boards=total_boards,
        total_cards=total_cards,
        total_lists=total_lists,
        cards_by_priority=cards_by_priority,
    )


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(auth.get_current_admin)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
