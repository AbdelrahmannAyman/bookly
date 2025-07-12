from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from starlette.responses import JSONResponse

from .Entity.models import User
from .Entity.schemas import UserCreate, UserUpdate, UserOut, UserLoginModel
from .service import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_all_users,
    update_user_by_id,
    delete_user_by_id
)
from src.config.database import get_db
from .utils import create_access_token, verify_password
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from src.config.redis import add_jti_to_blacklist

user_router = APIRouter()


@user_router.post("/signup/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user(user_data, db)


@user_router.post('/login/')
async def login_user_route(login_data: UserLoginModel, db: Session = Depends(get_db)):
    email = login_data.email
    password = login_data.password

    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        password_valid = verify_password(password, str(user.password))
        if password_valid:
            access_token = create_access_token(user_data={"email": user.email, "user_id": str(user.id)})
            refresh_token = create_access_token(user_data={"email": user.email, "user_id": str(user.id)},
                                                refresh=True, expiry=timedelta(days=2))
            return JSONResponse(
                content={
                    "message": "Login successfully ",
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, )
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")


@user_router.get('/refresh/')
async def refresh_token_route(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        access_token = create_access_token(user_data=token_details['user'], refresh=False)
        return JSONResponse(content={
            "access_token": access_token,
            "message": "Access token refreshed successfully"
        })

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")


@user_router.get('/me/')
async def get_current_user_route(user=Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@user_router.get('/logout/')
async def logout_user_route(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blacklist(jti)

    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )


@user_router.get("/users/", response_model=List[UserOut])
async def get_users_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_users(skip, limit, db)


@user_router.get("/user/id/{user_id}", response_model=UserOut)
async def get_user_by_id_route(user_id: str, db: Session = Depends(get_db)):
    return get_user_by_id(user_id, db)


@user_router.get("/user/email/{email}", response_model=UserOut)
async def get_user_by_email_route(email: str, db: Session = Depends(get_db)):
    return get_user_by_email(email, db)


@user_router.put("/user/{user_id}", response_model=UserOut)
async def update_user_route(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    return update_user_by_id(user_id, user_update, db)


@user_router.delete("/user/{user_id}")
async def delete_user_route(user_id: str, db: Session = Depends(get_db)):
    return delete_user_by_id(user_id, db)
