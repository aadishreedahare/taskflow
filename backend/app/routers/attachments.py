import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.config import settings
from app.database import get_db
from app.permissions import get_board_or_404, require_board_access

router = APIRouter(tags=["attachments"])


def _get_card_or_404(db: Session, card_id: int) -> models.Card:
    card = db.get(models.Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.post(
    "/cards/{card_id}/attachments", response_model=schemas.AttachmentOut, status_code=status.HTTP_201_CREATED
)
async def upload_attachment(
    card_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)

    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb}MB limit")

    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(settings.upload_dir, stored_name)
    with open(stored_path, "wb") as f:
        f.write(contents)

    attachment = models.Attachment(
        card_id=card_id,
        filename=file.filename or stored_name,
        filepath=stored_path,
        content_type=file.content_type,
        size_bytes=len(contents),
        uploaded_by=user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/cards/{card_id}/attachments", response_model=list[schemas.AttachmentOut])
def list_attachments(card_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    card = _get_card_or_404(db, card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)
    return card.attachments


@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    attachment = db.get(models.Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    card = _get_card_or_404(db, attachment.card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)
    if not os.path.exists(attachment.filepath):
        raise HTTPException(status_code=404, detail="File missing on server")
    return FileResponse(attachment.filepath, filename=attachment.filename, media_type=attachment.content_type)


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    attachment = db.get(models.Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    card = _get_card_or_404(db, attachment.card_id)
    board = get_board_or_404(db, card.task_list.board_id)
    require_board_access(db, board, user)

    if os.path.exists(attachment.filepath):
        os.remove(attachment.filepath)
    db.delete(attachment)
    db.commit()
