import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.config.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    publisher = Column(String, nullable=False, index=True)
    publisher_date = Column(DateTime, nullable=False, default=func.now())
    page_count = Column(Integer, nullable=False, index=True)
    language = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Book {self.title}>"