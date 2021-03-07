# pylint:disable=no-name-in-module, import-error
import app.api.utils_com as utils_com
from app import crud
from app.api.com.api_request_models import DeleteRequest, UpdateNameRequest
from fastapi import APIRouter

router = APIRouter()


@router.get("/api/classifier/fetch_all_rf", status_code=200)
async def fetch_all_rf_classifiers():
    """
    API request to return a list of all ComImage objects
    """
    clf_list = utils_com.get_com_clf_list(_type="rf_segmentation")
    return clf_list


@router.get("/api/classifier/fetch_rf_by_id/{classifier_uid}", status_code=200)
async def fetch_rf_classifier_by_id(
    classifier_uid: str
):
    """
    API request to return a single classifier by uid
    """
    classifier_uid = int(classifier_uid)
    classifier = utils_com.get_com_classifier_by_uid(classifier_uid)

    return classifier


@router.get("/api/classifier/fetch_all", status_code=200)
async def fetch_all_classifiers():
    """
    API request to return a list of all ComImage objects
    """
    clf_list = utils_com.get_com_clf_list(_type=None)
    return clf_list


@router.get("/api/classifier/fetch_all_df", status_code=200)
async def fetch_all_df_classifiers():
    """
    API request to return a list of all ComImage objects
    """
    clf_list = utils_com.get_com_clf_list(_type="deepflash_model")
    return clf_list


@router.get("/api/classifier/fetch_df_by_id/{classifier_uid}", status_code=200)
async def fetch_df_classifier_by_id(
    classifier_uid: str
):
    """
    API request to return a single classifier by uid
    """
    classifier_uid = int(classifier_uid)
    classifier = utils_com.get_com_classifier_by_uid(classifier_uid)
    return classifier


@router.post("/api/classifier/delete_by_id", status_code=200)
async def delete_classifier_by_id(delete_request: DeleteRequest):
    '''
    API request to delete a classifier
    '''
    classifier_uid = delete_request.id
    db_classifier = crud.read_db_classifier_by_uid(classifier_uid)
    db_classifier.delete()


@router.post("/api/classifier/update_name", status_code=200)
async def update_classifier_name(update_name_request: UpdateNameRequest):
    '''
    API Request to change a classifier name by uid
    '''
    classifier_uid = update_name_request.id
    new_name = update_name_request.new_name
    classifier = crud.read_db_classifier_by_uid(classifier_uid)
    classifier.update_name(new_name)
