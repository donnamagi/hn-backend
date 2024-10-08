# models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ARRAY,
    TIMESTAMP,
    event,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    deleted = Column(Boolean, nullable=True)
    type = Column(String(50), nullable=True)
    by = Column(String(255), nullable=True)
    time = Column(TIMESTAMP(timezone=True), nullable=True)
    text = Column(Text, nullable=True)
    dead = Column(Boolean, nullable=True)
    parent = Column(Integer, nullable=True)
    poll = Column(Integer, nullable=True)
    kids = Column(ARRAY(Integer), nullable=True)
    url = Column(String(255), nullable=True)
    score = Column(Integer, nullable=True)
    title = Column(String(255), nullable=True)
    parts = Column(ARRAY(Integer), nullable=True)
    descendants = Column(Integer, nullable=True)
    content_summary = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(
            timezone=True,
        ),
        server_default=func.now(),
        onupdate=func.now(),
    )
    category = Column(Integer, nullable=False)


@event.listens_for(Article, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = func.now()
    target.updated_at = func.now()


@event.listens_for(Article, "before_update")
def set_updated_at(mapper, connection, target):
    target.updated_at = func.now()


class Recent(Base):
    __tablename__ = "recents"
    id = Column(Integer, primary_key=True, index=True)
    best = Column(JSON, nullable=True)
    top = Column(JSON, nullable=True)
    new = Column(JSON, nullable=True)
    show = Column(JSON, nullable=True)
    ask = Column(JSON, nullable=True)
    job = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


@event.listens_for(Recent, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = func.now()
    target.updated_at = func.now()
