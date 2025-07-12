from redis.asyncio import from_url

token_blacklist = from_url('redis://localhost:6379/0')

async def add_jti_to_blacklist(jti: str) -> None:
    await token_blacklist.set(name=jti, value="", ex=3600)

async def token_in_blacklist(jti: str) -> bool:
    return await token_blacklist.get(name=jti) is not None
