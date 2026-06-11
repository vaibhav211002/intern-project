# Regulatory Document Manager

A lightweight document management system for regulatory PDFs (FDA, EMA, ICH, etc.).  
Upload PDFs, extract their text automatically, search across content, and organise with tags.

---

## Quick Start

### Option A — Docker (recommended, one command)

```bash
docker compose up --build
```

- Frontend → http://localhost:8501  
- API docs → http://localhost:8000/docs  
- The `seed` service auto-downloads 6 ICH/EMA PDFs on first run.

### Option B — Local (no Docker)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
bash start.sh                                        # starts API + seeds + Streamlit
```

Then open http://localhost:8501.

---

## Feature Overview

| Feature | Where |
|---|---|
| Upload PDF + extract text | `POST /documents/upload` |
| List documents (paginated) | `GET /documents?page=1&page_size=20` |
| Filter by tag | `GET /documents?tag=gcp` |
| Full-text + title keyword search | `GET /documents/search?q=pharmacokinetics` |
| Get single document with full text | `GET /documents/{id}` |
| Add tag | `POST /documents/{id}/tags` |
| Remove tag | `DELETE /documents/{id}/tags/{tag_name}` |
| List all tags | `GET /documents/tags/all` |

Interactive Swagger UI lives at `/docs` when the backend is running.

---

## Source Documents

Six publicly available ICH/EMA guidelines are seeded automatically:

| Document | Source |
|---|---|
| ICH Q1A(R2) — Stability Testing | ich.org |
| ICH Q8(R2) — Pharmaceutical Development | ich.org |
| ICH S1C(R2) — Carcinogenicity Studies | ich.org |
| ICH E6(R2) — Good Clinical Practice | ich.org |
| ICH E2A — Safety Data / Expedited Reporting | ema.europa.eu |
| ICH Q9 — Quality Risk Management | ema.europa.eu |

All are freely available under their respective public-access terms.

---

## Key Design Decisions

### Backend

**FastAPI + SQLAlchemy + SQLite**  
FastAPI gives automatic OpenAPI docs and async-ready handlers with minimal boilerplate. SQLAlchemy's ORM maps cleanly to the document/tag many-to-many relationship. SQLite requires zero infrastructure for a local/small-team tool and is swappable for Postgres via the `DATABASE_URL` env var.

**PyMuPDF for extraction**  
PyMuPDF (`fitz`) is consistently the fastest and most accurate pure-Python PDF parser for text-based PDFs, which is what regulatory guidelines are. Docling or Apache Tika would add value for scanned/OCR PDFs but introduce heavy JVM or ML-model dependencies not warranted here.

**Tags as a normalised table**  
Tags live in their own table (many-to-many via `document_tags`) rather than as a serialised string field. This allows efficient `filter by tag` queries and guarantees consistent capitalisation (all lowercased on write).

**Keyword search via SQL `ILIKE`**  
Simple `ILIKE %term%` over `title` and `full_text` columns. Fast enough for hundreds of documents in SQLite. The trade-off: no relevance ranking, no stemming, no multi-term AND/OR logic. See "What I'd add" below.

### Frontend

**Streamlit**  
Gets a functional UI with zero HTML/JS. The single-file `frontend/app.py` handles all three views (library, search, upload) plus an inline detail panel driven by `st.session_state`. The trade-off: Streamlit reruns the entire script on every interaction, so the detail panel is implemented as a bottom-of-page section rather than a true modal.

**Stateless API client**  
The frontend is a thin HTTP client — all state lives in the backend DB. This means the frontend can be scaled or replaced independently.

---

## Trade-offs

| Decision | What was traded away |
|---|---|
| SQLite default | Not suitable for concurrent multi-user writes at scale |
| ILIKE search | No ranking, stemming, or boolean operators |
| Streamlit frontend | Full-page reruns on every interaction; limited layout control |
| Text stored in DB | Large full-text columns; at scale, move text to object storage |
| Single-container SQLite | No horizontal scaling without switching to Postgres |

---

## What I'd Add With More Time

1. **Full-text search engine** — swap `ILIKE` for PostgreSQL `tsvector` full-text search or a lightweight Tantivy/Whoosh index. Add hit highlighting in the detail view.
2. **OCR support** — integrate Tesseract for scanned PDFs that return empty text.
3. **Chunked storage** — store extracted text in a separate `document_chunks` table (one row per page) for faster snippet-level retrieval.
4. **Authentication** — add JWT-based user accounts so each user manages their own document set.
5. **Async extraction** — offload PDF parsing to a Celery/ARQ background task and return a job ID immediately, avoiding request timeouts on large PDFs.
6. **Export / download** — let users download the extracted plain text alongside the original PDF.
7. **Better UX** — replace the Streamlit `st.rerun()` pattern with a React or HTMX frontend for true modal dialogs and optimistic updates.
8. **Test suite** — add `pytest` + `httpx` integration tests for all API endpoints.

---

## Project Structure

```
regulatory-doc-manager/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── db/database.py       # SQLAlchemy engine & session
│   ├── models/
│   │   ├── document.py      # ORM models (Document, Tag)
│   │   └── schemas.py       # Pydantic I/O schemas
│   ├── routers/documents.py # All REST endpoints
│   └── services/
│       └── pdf_extractor.py # PyMuPDF text extraction
├── frontend/
│   └── app.py               # Streamlit UI (single file)
├── scripts/
│   └── seed_documents.py    # Download + upload 6 ICH PDFs
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt
├── start.sh                 # One-command local dev start
└── README.md
```

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./regulatory_docs.db` | SQLAlchemy connection string |
| `API_BASE_URL` | `http://localhost:8000` | Frontend → backend base URL |
