from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
import os 


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regulatory_docs.db")
 
engine = create_engine(
    DATABASE_URL ,
    connect_args = {"check_same_thread":False}
    if "sqlite" in DATABASE_URL
    else{},
)

SessionLocal = sessionmaker(
    autocommit=False ,
    autoflush=False ,
    bind= engine
)


def startdb():
    db = SessionLocal() 
    try :
        yield db
    finally :
        db.close()



def init_db():
    from backend.models.document import Base
    Base.metadata.create_all(bind=engine)
    
    














