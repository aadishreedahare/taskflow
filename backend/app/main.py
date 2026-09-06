from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 (ensures models are registered before create_all)
from app.routers import auth_router, boards, lists, cards, attachments, search, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="A Trello-style task/project management API built with FastAPI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(boards.router)
app.include_router(lists.router)
app.include_router(cards.router)
app.include_router(attachments.router)
app.include_router(search.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "taskflow-api"}
