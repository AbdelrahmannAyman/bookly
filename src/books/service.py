from sqlalchemy.orm import Session
from fastapi import HTTPException
from .Entity import models, schemas


def create_book(book_data: schemas.BookCreate, db: Session) -> models.Book:
    book_dict = book_data.model_dump()
    if book_dict.get('publisher_date') is None:
        book_dict.pop('publisher_date', None)

    db_book = models.Book(**book_dict)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_all_books(skip: int, limit: int, db: Session) -> list[type[models.Book]]:
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book_by_id(book_id: str, db: Session) -> models.Book:
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def delete_book_by_id(book_id: str, db: Session) -> None:
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()


def update_book_by_id(book_id: str, book_update: schemas.BookCreate, db: Session) -> models.Book:
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_dict = book_update.model_dump()
    for field, value in update_dict.items():
        if field != 'publisher_date' or value is not None:
            setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book
