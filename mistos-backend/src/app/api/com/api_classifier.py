from fastapi import APIRouter
import app.api.utils_com as utils_com

import asyncio

router = APIRouter()


@router.get("/api/classifier/fetch_all", status_code=200)
async def fetch_all_classifiers():
    """
    API request to return a list of all ComImage objects
    """
    clf_list = utils_com.get_com_clf_list()
    return clf_list

@router.get("/api/classifier/fetch_by_id/{classifier_uid}", status_code=200)
async def fetch_classifier_by_id(
    classifier_uid:str
):
    """
    API request to return a single classifier by uid
    """
    classifier_uid = int(classifier_uid)
    classifier = utils_com.get_com_classifier_by_uid(classifier_uid)
    print(classifier)
    return classifier