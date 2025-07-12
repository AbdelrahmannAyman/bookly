from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .utils import generate_hashed_password
from .Entity.models import User
from .Entity.schemas import UserCreate, UserUpdate, UserOut
from typing import List


def create_user(user_data: UserCreate, db: Session) -> UserOut:
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = generate_hashed_password(user_data.password)
    user = User(**user_data.model_dump(exclude={"password"}), password=hashed_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


def get_user_by_email(email: EmailStr, db: Session) -> UserOut:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


def get_user_by_id(user_id: str, db: Session) -> UserOut:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


def get_all_users(skip: int, limit: int, db: Session) -> List[UserOut]:
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserOut.model_validate(u) for u in users]


def delete_user_by_id(user_id: str, db: Session) -> dict[str, str]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


def update_user_by_id(user_id: str, user_update: UserUpdate, db: Session) -> UserOut:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
