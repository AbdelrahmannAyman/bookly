from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.books.Entity import schemas
from src.config.database import get_db
from src.books.service import (
    create_book,
    get_all_books,
    get_book_by_id,
    delete_book_by_id,
    update_book_by_id
)
from src.auth.dependencies import AccessTokenBearer

book_router = APIRouter()
access_token_bearer = AccessTokenBearer()


@book_router.post("/", response_model=schemas.Book, status_code=201)
async def create_books(book_data: schemas.BookCreate, db: Session = Depends(get_db),
                       user_details=Depends(access_token_bearer)):
    return create_book(book_data, db)


@book_router.get("/", response_model=List[schemas.Book])
async def fetch_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                      user_details=Depends(access_token_bearer)):
    return get_all_books(skip, limit, db)


@book_router.get("/{book_id}", response_model=schemas.Book)
async def fetch_book(book_id: str, db: Session = Depends(get_db),
                     user_details=Depends(access_token_bearer)):
    return get_book_by_id(book_id, db)


@book_router.delete("/{book_id}")
async def delete_book(book_id: str, db: Session = Depends(get_db),
                      user_details=Depends(access_token_bearer)):
    delete_book_by_id(book_id, db)
    return {"message": "Book deleted successfully"}


@book_router.put("/{book_id}", response_model=schemas.Book)
async def update_book(book_id: str, book_update: schemas.BookCreate, db: Session = Depends(get_db),
                      user_details=Depends(access_token_bearer)):
    return update_book_by_id(book_id, book_update, db)
