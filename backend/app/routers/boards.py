from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.permissions import get_board_or_404, require_board_access, require_board_owner

router = APIRouter(prefix="/boards", tags=["boards"])


def _board_to_detail(board: models.Board) -> schemas.BoardDetailOut:
    members = [
        schemas.MemberOut(
            id=m.id, user_id=m.user_id, username=m.user.username, email=m.user.email, role=m.role
        )
        for m in board.members
    ]
    lists = []
    for lst in board.lists:
        cards = []
        for c in lst.cards:
            cards.append(
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
            )
        lists.append(
            schemas.ListOut(id=lst.id, board_id=lst.board_id, title=lst.title, position=lst.position, cards=cards)
        )
    return schemas.BoardDetailOut(
        id=board.id,
        title=board.title,
        description=board.description,
        owner_id=board.owner_id,
        created_at=board.created_at,
        lists=lists,
        labels=[schemas.LabelOut.model_validate(l) for l in board.labels],
        members=members,
    )


@router.get("", response_model=list[schemas.BoardOut])
def list_boards(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    boards = (
        db.query(models.Board)
        .outerjoin(models.BoardMember)
        .filter(or_(models.Board.owner_id == user.id, models.BoardMember.user_id == user.id))
        .distinct()
        .all()
    )
    return boards


@router.post("", response_model=schemas.BoardOut, status_code=status.HTTP_201_CREATED)
def create_board(
    payload: schemas.BoardCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    board = models.Board(title=payload.title, description=payload.description, owner_id=user.id)
    db.add(board)
    db.commit()
    db.refresh(board)

    # Seed with the classic three columns so a new board isn't empty.
    for i, title in enumerate(["To Do", "In Progress", "Done"]):
        db.add(models.TaskList(board_id=board.id, title=title, position=i))
    db.commit()
    db.refresh(board)
    return board


@router.get("/{board_id}", response_model=schemas.BoardDetailOut)
def get_board(board_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    board = get_board_or_404(db, board_id)
    require_board_access(db, board, user)
    return _board_to_detail(board)


@router.patch("/{board_id}", response_model=schemas.BoardOut)
def update_board(
    board_id: int,
    payload: schemas.BoardUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    board = get_board_or_404(db, board_id)
    require_board_owner(board, user)
    if payload.title is not None:
        board.title = payload.title
    if payload.description is not None:
        board.description = payload.description
    db.commit()
    db.refresh(board)
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    board = get_board_or_404(db, board_id)
    require_board_owner(board, user)
    db.delete(board)
    db.commit()


@router.post("/{board_id}/members", response_model=schemas.MemberOut, status_code=status.HTTP_201_CREATED)
def invite_member(
    board_id: int,
    payload: schemas.MemberInvite,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    board = get_board_or_404(db, board_id)
    require_board_owner(board, user)

    invitee = db.query(models.User).filter(models.User.email == payload.email).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="No user with that email")
    if invitee.id == board.owner_id:
        raise HTTPException(status_code=400, detail="User already owns this board")
    if any(m.user_id == invitee.id for m in board.members):
        raise HTTPException(status_code=400, detail="User is already a member")

    member = models.BoardMember(board_id=board.id, user_id=invitee.id, role=models.BoardRole.member)
    db.add(member)
    db.commit()
    db.refresh(member)
    return schemas.MemberOut(
        id=member.id, user_id=invitee.id, username=invitee.username, email=invitee.email, role=member.role
    )


@router.delete("/{board_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    board_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    board = get_board_or_404(db, board_id)
    require_board_owner(board, user)
    member = db.get(models.BoardMember, member_id)
    if not member or member.board_id != board_id:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()


@router.post("/{board_id}/labels", response_model=schemas.LabelOut, status_code=status.HTTP_201_CREATED)
def create_label(
    board_id: int,
    payload: schemas.LabelCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    board = get_board_or_404(db, board_id)
    require_board_access(db, board, user)
    label = models.Label(board_id=board_id, name=payload.name, color=payload.color)
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


@router.delete("/{board_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(
    board_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    board = get_board_or_404(db, board_id)
    require_board_access(db, board, user)
    label = db.get(models.Label, label_id)
    if not label or label.board_id != board_id:
        raise HTTPException(status_code=404, detail="Label not found")
    db.delete(label)
    db.commit()
