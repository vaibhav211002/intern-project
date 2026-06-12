# Regulatory Document Manager

A full-stack web application for ingesting, browsing, searching, and tagging regulatory PDFs (FDA, EMA, ICH guidelines).

---

## Quick Start

**Prerequisites:** Python 3.10, 3.11, or 3.12

**Step 1 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2 — Start the backend** (Terminal 1)
```bash
cd regulatory-doc-manager
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Step 3 — Seed sample documents** (Terminal 2)
```bash
cd regulatory-doc-manager
python scripts/seed_documents.py
```

**Step 4 — Start the frontend** (Terminal 2, after seeding)
```bash
python -m streamlit run frontend/app.py --server.port 8501
```

**Step 5 — Open the app**
```
http://localhost:8501
```

---

## How to Use the App

| Action | How |
|---|---|
| Browse all documents | **Document Library** tab in the sidebar |
| Filter by tag | Use the tag dropdown in the left sidebar |
| Search by keyword | **Search** tab — searches titles and full extracted text |
| View full document text | Click **Open →** on any document card |
| Add a tag to a document | Open a document → type in "Add a tag" box → click Add |
| Remove a tag | Open a document → select tag from "Remove a tag" dropdown |
| Upload your own PDF | **Upload PDF** tab — supports any text-based PDF |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/documents/upload` | Upload a PDF, extract text, assign tags |
| `GET` | `/documents` | List all documents (paginated, filterable by tag) |
| `GET` | `/documents/search?q=term` | Keyword search across title and full text |
| `GET` | `/documents/{id}` | Get a single document with full text |
| `POST` | `/documents/{id}/tags` | Add a tag to a document |
| `DELETE` | `/documents/{id}/tags/{tag}` | Remove a tag from a document |
| `GET` | `/documents/tags/all` | List all tags in the system |

Interactive Swagger UI available at `http://localhost:8000/docs`.

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend framework | **FastAPI** | REST API, automatic OpenAPI docs, async support |
| ORM | **SQLAlchemy** | Database models and queries |
| Database | **SQLite** | Zero-config local storage (swappable to Postgres) |
| PDF extraction | **PyMuPDF** | Fast, accurate text extraction from PDF files |
| Data validation | **Pydantic** | Request/response schema validation |
| Frontend | **Streamlit** | Python-only UI — no HTML/JS required |
| HTTP client | **requests** | Frontend → backend API calls |

---

## Source Documents (Auto-seeded)

Six publicly available ICH/EMA guidelines are downloaded and uploaded automatically on first run:

| Document | Tags | Source |
|---|---|---|
| ICH Q1A(R2) — Stability Testing of New Drug Substances | `ich, quality, stability` | ich.org |
| ICH Q8(R2) — Pharmaceutical Development | `ich, quality, pharmaceutical-development` | ich.org |
| ICH S1C(R2) — Dose Selection for Carcinogenicity Studies | `ich, safety, carcinogenicity` | ich.org |
| ICH E6(R2) — Good Clinical Practice | `ich, efficacy, gcp, clinical-trials` | ich.org |
| ICH E2A — Clinical Safety Data / Expedited Reporting | `ich, ema, safety, pharmacovigilance` | ema.europa.eu |
| ICH Q9 — Quality Risk Management | `ich, ema, quality, risk-management` | ema.europa.eu |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / User                        │
└───────────────────────┬─────────────────────────────────┘
                        │  HTTP (port 8501)
┌───────────────────────▼─────────────────────────────────┐
│              Streamlit Frontend (frontend/app.py)        │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Document   │  │    Search    │  │  Upload PDF    │  │
│  │  Library    │  │    Page      │  │  Page          │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                                          │
│              requests (HTTP calls to API)                │
└───────────────────────┬─────────────────────────────────┘
                        │  HTTP (port 8000)
┌───────────────────────▼─────────────────────────────────┐
│               FastAPI Backend                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           routers/documents.py                   │   │
│  │  POST /upload  GET /  GET /search  GET /{id}     │   │
│  │  POST /{id}/tags   DELETE /{id}/tags/{tag}       │   │
│  └───────────────────────┬──────────────────────────┘   │
│                          │                               │
│  ┌───────────────────────▼──────────────────────────┐   │
│  │           services/pdf_extractor.py              │   │
│  │           PyMuPDF — extract text from PDF        │   │
│  └───────────────────────┬──────────────────────────┘   │
│                          │                               │
│  ┌───────────────────────▼──────────────────────────┐   │
│  │           SQLAlchemy ORM                         │   │
│  │   models: Document, Tag, document_tags (M2M)     │   │
│  └───────────────────────┬──────────────────────────┘   │
│                          │                               │
│  ┌───────────────────────▼──────────────────────────┐   │
│  │           SQLite Database                        │   │
│  │           regulatory_docs.db                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Request Flow

```
User types keyword in Search box
        │
        ▼
Streamlit reruns app.py
        │
        ▼
requests.get("http://backend:8000/documents/search?q=pharmacokinetics")
        │
        ▼
FastAPI router receives GET /documents/search
        │
        ▼
SQLAlchemy runs: SELECT * FROM documents WHERE title ILIKE '%pharmacokinetics%'
                                           OR full_text ILIKE '%pharmacokinetics%'
        │
        ▼
Pydantic validates and serialises results → JSON response
        │
        ▼
Streamlit renders document cards with tags on screen
```

---

## Folder Structure

```
regulatory-doc-manager/
│
├── backend/                        # FastAPI application
│   ├── __init__.py
│   ├── main.py                     # App entry point — creates FastAPI app,
│   │                               # registers middleware, mounts router
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py             # SQLAlchemy engine, session factory,
│   │                               # init_db() to create tables on startup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py             # ORM models: Document, Tag, document_tags
│   │   │                           # (many-to-many join table)
│   │   └── schemas.py              # Pydantic schemas for request/response
│   │                               # validation and JSON shaping
│   ├── routers/
│   │   ├── __init__.py
│   │   └── documents.py            # All 7 REST endpoints — upload, list,
│   │                               # search, get, add tag, remove tag, list tags
│   └── services/
│       ├── __init__.py
│       └── pdf_extractor.py        # PyMuPDF wrapper — takes PDF bytes,
│                                   # returns (full_text, page_count)
│
├── frontend/
│   └── app.py                      # Entire Streamlit UI in one file
│                                   # Handles: Library, Search, Upload views
│                                   # + inline document detail with tag controls
│
├── scripts/
│   └── seed_documents.py           # Downloads 6 ICH/EMA PDFs from public URLs
│                                   # and uploads them via the API on first run
│
├── requirements.txt                # All Python dependencies
├── runtime.txt                     # Pins Python 3.11 for Render deployment
├── start.sh                        # One-command local dev launcher
└── README.md                       # This file
```

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./regulatory_docs.db` | SQLAlchemy DB connection string — set to `postgresql://...` for Postgres |
| `API_BASE_URL` | `http://localhost:8000` | Frontend → backend base URL (set to Render URL in production) |

---

## Key Design Decisions

### FastAPI over Flask
FastAPI provides automatic OpenAPI/Swagger documentation at `/docs` with zero extra code, built-in Pydantic validation, and async support. Flask would have required manual schema documentation and a separate validation library.

### PyMuPDF over Docling
PyMuPDF (`fitz`) extracts text from text-based PDFs in milliseconds with no external dependencies. Docling and Apache Tika are more powerful for scanned/mixed PDFs but introduce JVM or heavy ML-model dependencies that aren't justified for ICH/FDA guidelines which are always text-based.

### Tags as a normalised table
Tags live in their own `tags` table connected via a `document_tags` join table rather than stored as a comma-separated string. This enables efficient `filter by tag` SQL queries, prevents duplicates, and keeps tag names consistently lowercased.

### SQLite with Postgres upgrade path
SQLite requires zero infrastructure and works out of the box. Swapping to Postgres requires only changing the `DATABASE_URL` environment variable — no code changes needed.

### Streamlit for the frontend
Delivers a fully functional, styled UI in pure Python with no HTML, CSS, or JavaScript required. The trade-off is that Streamlit reruns the entire script on every user interaction, which makes true modal dialogs impossible — the document detail panel is rendered as a bottom-of-page section instead.

---

## Trade-offs

| Decision | What was traded away |
|---|---|
| SQLite default | Not safe for concurrent multi-user writes at scale |
| `ILIKE` keyword search | No relevance ranking, stemming, or boolean AND/OR |
| Streamlit frontend | Full page reruns on every click; no true modals |
| Full text stored in DB | At scale, large text columns; better moved to object storage |
| Synchronous PDF extraction | Large PDFs block the upload request; needs background tasks at scale |

---

## What I'd Add With More Time

1. **Proper full-text search** — PostgreSQL `tsvector` or a Whoosh/Tantivy index with hit highlighting and relevance ranking
2. **OCR support** — Tesseract integration for scanned PDFs that return empty text
3. **Async PDF extraction** — Celery/ARQ background task so large uploads return immediately with a job status URL
4. **Authentication** — JWT-based user accounts so each user has their own document workspace
5. **Chunked text storage** — One row per page in a `document_chunks` table for faster snippet-level retrieval
6. **Test suite** — `pytest` + `httpx` integration tests covering all endpoints including edge cases (no results, duplicate tags, oversized files)
7. **React frontend** — Replace Streamlit with a proper React UI for true modals, optimistic updates, and better mobile experience
