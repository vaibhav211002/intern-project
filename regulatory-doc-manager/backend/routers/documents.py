from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional

from backend.db.database import startdb
from backend.models.document import Document, Tag
from backend.models.schemas import (
    DocumentOut,
    DocumentDetail,
    PaginatedDocuments,
    TagRequest,
    TagOut,
)
from backend.services.pdf_extractor import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])


# ── helpers ──────────────────────────────────────────────────────────────────

def get_or_create_tag(db: Session, name: str) -> Tag:
    name = name.strip().lower()
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        db.flush()
    return tag


# ── endpoints ────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    tags: Optional[str] = Form(""),          # comma-separated
    db: Session = Depends(startdb),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:     # 50 MB guard
        raise HTTPException(status_code=413, detail="File too large (max 50 MB).")

    full_text, page_count = extract_text(contents)

    doc_title = (title or file.filename.removesuffix(".pdf")).strip() or file.filename
    doc = Document(
        title=doc_title,
        filename=file.filename,
        full_text=full_text,
        page_count=page_count,
    )
    db.add(doc)
    db.flush()

    for raw_tag in (tags or "").split(","):
        clean = raw_tag.strip()
        if clean:
            doc.tags.append(get_or_create_tag(db, clean))

    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=PaginatedDocuments)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None),
    db: Session = Depends(startdb),
):
    q = db.query(Document)
    if tag:
        q = q.join(Document.tags).filter(func.lower(Tag.name) == tag.strip().lower())
    total = q.count()
    items = (
        q.order_by(Document.upload_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedDocuments(total=total, page=page, page_size=page_size, items=items)


@router.get("/search", response_model=PaginatedDocuments)
def search_documents(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(startdb),
):
    pattern = f"%{q}%"
    query = db.query(Document).filter(
        or_(
            Document.title.ilike(pattern),
            Document.full_text.ilike(pattern),
        )
    )
    total = query.count()
    items = (
        query.order_by(Document.upload_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedDocuments(total=total, page=page, page_size=page_size, items=items)


@router.get("/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: int, db: Session = Depends(startdb)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.post("/{doc_id}/tags", response_model=DocumentOut)
def add_tag(doc_id: int, body: TagRequest, db: Session = Depends(startdb)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    tag = get_or_create_tag(db, body.tag)
    if tag not in doc.tags:
        doc.tags.append(tag)
        db.commit()
        db.refresh(doc)
    return doc


@router.delete("/{doc_id}/tags/{tag_name}", response_model=DocumentOut)
def remove_tag(doc_id: int, tag_name: str, db: Session = Depends(startdb)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    tag = db.query(Tag).filter(func.lower(Tag.name) == tag_name.strip().lower()).first()
    if tag and tag in doc.tags:
        doc.tags.remove(tag)
        db.commit()
        db.refresh(doc)
    return doc


@router.get("/tags/all", response_model=list[TagOut])
def list_all_tags(db: Session = Depends(startdb)):
    return db.query(Tag).order_by(Tag.name).all()
