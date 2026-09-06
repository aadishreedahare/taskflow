from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models


def get_board_or_404(db: Session, board_id: int) -> models.Board:
    board = db.get(models.Board, board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


def require_board_access(db: Session, board: models.Board, user: models.User) -> None:
    """Raise 403 unless the user owns the board or is a member of it."""
    if board.owner_id == user.id:
        return
    is_member = any(m.user_id == user.id for m in board.members)
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this board")


def require_board_owner(board: models.Board, user: models.User) -> None:
    if board.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the board owner can do this")
