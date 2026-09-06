# TaskFlow

A full-stack, Trello-style task and project management app. Built as a portfolio project to
demonstrate a complete web application: authentication, relational data modeling, a REST API,
a dynamic drag-and-drop frontend, file uploads, search/filtering, and role-based access.

## Features

- **Auth**: register/login with JWT, passwords hashed with bcrypt
- **Boards**: create boards, invite members by email, board-level access control (owner vs member)
- **Lists & cards**: Trello-style columns and cards with drag-and-drop reordering (within and
  across lists), backed by real API calls that persist the new order
- **Card details**: description, priority, due date, labels, comments, file attachments
- **Search & filtering**: full-text search across every card you have access to, filterable by
  priority
- **Admin dashboard**: usage stats, user list, board list, restricted to the first registered
  account (auto-promoted to admin) or anyone flagged `is_admin`
- **Tests**: pytest suite covering auth, board access control, and card workflows

## Tech stack

| Layer    | Choice                                             |
|----------|-----------------------------------------------------|
| Frontend | React 18 (Vite), React Router, Tailwind CSS, [@hello-pangea/dnd](https://github.com/hello-pangea/dnd) for drag-and-drop, Axios |
| Backend  | FastAPI, SQLAlchemy 2.0, Pydantic v2, python-jose (JWT), passlib (bcrypt) |
| Database | SQLite by default (zero setup) — swap `DATABASE_URL` for Postgres/MySQL in production |
| Tests    | pytest + FastAPI's `TestClient`, an isolated SQLite file per test run |

## Project structure

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, router registration, CORS
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # password hashing, JWT issue/verify
│   │   ├── permissions.py   # board access-control helpers
│   │   ├── config.py        # settings (env-driven)
│   │   ├── database.py      # engine/session setup
│   │   └── routers/         # auth, boards, lists, cards, attachments, search, admin
│   ├── tests/                # pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js         # axios instance + auth header injection
│   │   ├── context/AuthContext.jsx
│   │   ├── components/           # Navbar, ListColumn, CardItem, CardModal, ProtectedRoute
│   │   └── pages/                 # Login, Register, Dashboard, BoardView, SearchResults, AdminPanel
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit SECRET_KEY for anything beyond local demos
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000` (interactive docs at `/docs`). A SQLite file
(`taskflow.db`) and an `uploads/` folder are created automatically on first run.

Run the test suite:

```bash
pytest
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # defaults to http://localhost:8000, edit if needed
npm run dev
```

Open `http://localhost:5173`. Register an account — the **first user to register becomes an
admin** automatically, so you'll immediately see the Admin link in the navbar.

### With Docker

```bash
docker compose up --build
```

Backend on `:8000`, frontend on `:5173`.

## How it works

- **Boards → Lists → Cards**: a board is seeded with "To Do / In Progress / Done" lists on
  creation. Dragging a card (via `@hello-pangea/dnd`) updates local state immediately and fires
  `PATCH` requests to persist the new `list_id`/`position` for every affected card, so a page
  refresh preserves the order. Dragging a list column reorders the same way.
- **Access control**: every board/list/card/comment/attachment endpoint resolves the owning
  board and checks the caller is either the owner or an invited member before doing anything —
  see `app/permissions.py`.
- **File uploads**: attachments are streamed to `backend/uploads/` under a random filename (the
  original name is kept in the DB for display/download) and served back through an authenticated
  download endpoint rather than a public static path.
- **Search**: `/search/cards` scopes results to boards the caller can access, then applies an
  `ILIKE` text match plus optional priority/board/label filters.

## Notes on this build

This project was scaffolded and written in a sandboxed environment without package-registry
network access, so `pip install` / `npm install` could not be executed live here. Every Python
file was verified to compile (`python3 -m py_compile`), and every frontend file was verified with
`esbuild` (full JSX parse + local-import resolution). The pytest suite is included and ready to
run — it should pass out of the box once you `pip install -r requirements.txt` locally, since it
follows the same patterns exercised in the API code. Please run `pytest` and `npm run build`
after installing dependencies to confirm before you rely on this for an interview demo.

## Ideas for extending this further

- Real-time updates via WebSockets (so board changes sync live across members)
- Postgres + Alembic migrations for a production-shaped setup
- Card checklists / subtasks
- Activity log per card ("Alice moved this to Done")
- Deploy: Render/Railway for the API, Vercel/Netlify for the frontend
