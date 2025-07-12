from datetime import timedelta, datetime, timezone
import jwt
import uuid

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)


def generate_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    expire_time = datetime.now(timezone.utc) + (
        expiry if expiry else (REFRESH_TOKEN_EXPIRE if refresh else ACCESS_TOKEN_EXPIRE)
    )

    payload = {
        'jti': str(uuid.uuid4()),
        'user': user_data,
        'exp': int(expire_time.timestamp()),
        'refresh': refresh,
        'token_type': 'refresh' if refresh else 'access'
    }

    token = jwt.encode(payload, key="cd145bb3c122351c25737bb11f4961d4", algorithm="HS256")
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key="cd145bb3c122351c25737bb11f4961d4",
            algorithms=["HS256"]
        )
        return token_data
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
