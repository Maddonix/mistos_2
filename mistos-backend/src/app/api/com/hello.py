from fastapi import APIRouter

import asyncio

router = APIRouter()


@router.get("/api/hello", status_code=200)
async def hello():
    """
    The alive-endpoint. It returns a static JSON.
    """
    return {"hello": "I am Mistos!"}