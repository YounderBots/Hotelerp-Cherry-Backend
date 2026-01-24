from datetime import datetime, timedelta
from typing import Any, Dict, Optional
 
import bcrypt
import httpx
from configs import BaseConfig
from jose import jwt
 
 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, BaseConfig.SECRET_KEY, algorithm=BaseConfig.ALGORITHM
    )
    return encoded_jwt
 
 
async def fetch_from_service(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 5.0,
) -> Any:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


async def call_service(
    method: str,
    url: str,
    headers: dict = None,
    data: dict = None,
    params: dict = None,
    timeout: float = 5.0
):
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        )
        response.raise_for_status()
        return response.json()

