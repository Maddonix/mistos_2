from fastapi import APIRouter, Depends
from app.api.dependencies import get_db
from sqlalchemy.orm import Session
import app.db_models as db_models
import asyncio

router = APIRouter()


@router.get("/api/hello", status_code=200)
async def hello():
    """
    The alive-endpoint. It returns a static JSON.
    """
    return {"hello": "I am Mistos!"}

@router.get("/api/test_get_imagelist", status_code=200)
async def fetch_all_images(sess: Session = Depends(get_db)):
    """
    API request to return a list of all images

    Parameters:

        - sess(sqlalchemy.orm.Session): The database session to be used
    """
    sql_image_list = [_ for _ in sess.query(db_models.Image)]
    return sql_image_list
