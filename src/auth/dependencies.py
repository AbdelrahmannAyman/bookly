from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.auth.utils import decode_token
from src.config.database import get_db
from src.config.redis import token_in_blacklist
from src.auth.service import get_user_by_email

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not await self.token_valid(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        if await token_in_blacklist(token_data['jti']):
            raise HTTPException(status_code=401, detail="This token is invalid or has been revoked")

        await self.verify_token_data(token_data)

        return token_data

    async def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        return token_data is not None

    async def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    async def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(status_code=401, detail="Please provide a valid access token")


class RefreshTokenBearer(TokenBearer):
    async def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(status_code=401, detail="Please provide a valid refresh token")


def get_current_user(token_details: dict=Depends(AccessTokenBearer()), db: Session = Depends(get_db)):
    user_email = token_details['user']['email']
    user = get_user_by_email(user_email, db)
    return user