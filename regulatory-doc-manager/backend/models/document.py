from sqlalchemy import Column , Integer , String , Text , DateTime , Table , ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from datetime import datetime


Base = declarative_base() 
# join table code 


document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)




class Document(Base):
     __tablename__  = "documents"
     id = Column(Integer,primary_key=True , index=True)
     title = Column(String(512) , nullable=False , index=True)
     filename = Column(String(512), nullable= False)
     upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
     full_text = Column(Text, nullable=False, default="")
     page_count = Column(Integer, default=0)
     tags = relationship(
         "Tag", 
         secondary=document_tags, 
         back_populates="documents"
    )
     
     
class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer,primary_key=True , index=True)
    name = Column(String(128) , unique=True , nullable=False , index = True)
    documents = relationship(
        "Document",
        secondary = document_tags,
        back_populates="tags"
    )






























































# from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# document_tags = Table(
#     "document_tags",
#     Base.metadata,
#     Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
# )


# class Document(Base):
#     __tablename__ = "documents"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(512), nullable=False, index=True)
#     filename = Column(String(512), nullable=False)
#     upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
#     full_text = Column(Text, nullable=False, default="")
#     page_count = Column(Integer, default=0)

#     tags = relationship("Tag", secondary=document_tags, back_populates="documents")


# class Tag(Base):
#     __tablename__ = "tags"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(128), unique=True, nullable=False, index=True)

#     documents = relationship("Document", secondary=document_tags, back_populates="tags")
