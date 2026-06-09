from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



from backend.db.database import init_db
from backend.routers.documents import router as docs_router


app = FastAPI(
    title="Regulatory Document Manager",
    description="Upload, search and tag pdfs",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(docs_router)


@app.get("/health")
def health():
    return{"status" : "ok"}






































# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from backend.db.database import init_db
# from backend.routers.documents import router as docs_router

# app = FastAPI(
#     title="Regulatory Document Manager",
#     description="Upload, search and tag regulatory PDFs (FDA, EMA, ICH, etc.)",
#     version="1.0.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.on_event("startup")
# def on_startup():
#     init_db()


# app.include_router(docs_router)


# @app.get("/health")
# def health():
#     return {"status": "ok"}
