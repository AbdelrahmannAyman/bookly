from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routers import user_router
from contextlib import asynccontextmanager

from src.books.Entity import models
from src.config.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        raise
    yield
    print("🛑 Application shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(book_router, prefix="/books", tags=["books"])
app.include_router(user_router, prefix="", tags=["users"])
