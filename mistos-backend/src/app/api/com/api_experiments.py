# pylint:disable=no-name-in-module, import-error
from fastapi import APIRouter, Response
import app.api.utils_com as utils_com
import app.api.utils_export as utils_export
import app.api.utils_import as utils_import
import pathlib
from app import crud
from app.api.classes import DbExperiment
from app.api.com.api_request_models import (CreateExperimentRequest, DeleteExperimentGroupRequest, NewExperimentGroupRequest,
                                            DeleteExperimentRequest, UpdateHintRequest, UpdateDescriptionRequest, UpdateNameRequest, UpdateExperimentGroupImagesRequest,
                                            DeleteImageFromExperimentGroupRequest, AddLayerToGroupRequest, ReadFromPathRequest, CalculateExperimentResultsRequest, ExportExperimentRequest)


router = APIRouter()

# Get


@router.get("/api/experiments/fetch_all", status_code=200)
async def fetch_all_experiments():
    """
    API request to return a list of all Experiments
    """
    experiment_list = utils_com.get_com_experiment_list()
    return experiment_list


@router.get("/api/experiments/fetch_by_id/{experiment_uid}", status_code=200)
async def fetch_experiment_by_id(
    experiment_uid: str
):
    """
    API request to return a single experiment by uid
    """
    experiment_uid = int(experiment_uid)
    experiment = utils_com.get_com_experiment_by_uid(experiment_uid)
    return experiment

# Post


@router.post("/api/experiments/create_new_experiment", status_code=201)
async def create_experiment(data: CreateExperimentRequest):
    '''
    API request to create a new experiment
    '''
    db_experiment_kwargs = data.experiment.dict()
    db_experiment = DbExperiment(**db_experiment_kwargs)
    db_experiment.create_in_db()
    print("api experiments, create experiment:")
    print(db_experiment)


@router.post("/api/experiments/new_group_by_id", status_code=201)
async def new_experiment_group_by_id(new_experiment_group_request: NewExperimentGroupRequest):
    '''
    API request to create a new experiment group. Expects an 
    '''
    print("api experiments_delete experiment group")
    print(new_experiment_group_request)
    db_experiment = crud.read_experiment_by_uid(
        new_experiment_group_request.experiment_id)
    int_experiment = db_experiment.to_int_class()
    print(int_experiment)
    # Maybe implement name from frontend
    int_experiment.add_experiment_group("NEW EXPERIMENT GROUP")


@router.post("/api/experiments/delete_group_by_id", status_code=200)
async def delete_experiment_group_by_id(delete_experiment_group_request: DeleteExperimentGroupRequest):
    '''
    API request to delete an experiment group. Expects an DeleteExperimentGroupRequest
    '''
    db_experiment = crud.read_experiment_by_uid(
        delete_experiment_group_request.experiment_id)
    db_experiment.delete_experiment_group(
        delete_experiment_group_request.group_id)


@router.post("/api/experiments/delete_by_id", status_code=200)
async def delete_experiment_by_id(delete_experiment_request: DeleteExperimentRequest):
    '''
    API request to delete an experiment. Expects an DeleteExperimentRequest
    '''
    db_experiment = crud.read_experiment_by_uid(
        delete_experiment_request.experiment_id)
    db_experiment.delete()


@router.post("/api/experiments/update_experiment_name", status_code=200)
async def update_experiment_name(update_name_request: UpdateNameRequest):
    '''
    API Request to update an experiment Name
    '''
    db_experiment = crud.read_experiment_by_uid(update_name_request.id)
    db_experiment.update_name(update_name_request.new_name)


@router.post("/api/experiments/calculate_results", status_code=200)
async def calculate_experiment_results(calculate_results_request: CalculateExperimentResultsRequest):
    '''
    API request to calculate results of all experiment groups of an experiment. Expects CalculateExperimentResultsRequest.
    '''
    print("api calculate_experiment_results")
    db_experiment = crud.read_experiment_by_uid(
        calculate_results_request.experiment_id)
    int_experiment = db_experiment.to_int_class()
    int_experiment.calculate_results()


@router.post("/api/experiments/update_experiment_hint", status_code=200)
async def update_experiment_hint(update_hint_request: UpdateHintRequest):
    '''
    API Request to update an experiment Hint
    '''
    db_experiment = crud.read_experiment_by_uid(update_hint_request.id)
    db_experiment.update_hint(update_hint_request.new_hint)


@router.post("/api/experiments/update_experiment_description", status_code=200)
async def update_experiment_description(update_description_request: UpdateDescriptionRequest):
    '''
    API Request to update an experiment description
    '''
    db_experiment = crud.read_experiment_by_uid(update_description_request.id)
    db_experiment.update_description(
        update_description_request.new_description)


@router.post("/api/experiments/add_result_layer_to_group", status_code=200)
async def add_result_layer_to_group(add_layer_to_group_request: AddLayerToGroupRequest):
    '''
    API Request to update an experiment_group active layer list
    '''
    db_experiment_group = crud.read_experiment_db_group_by_uid(
        add_layer_to_group_request.group_id)
    db_experiment_group.add_result_layer(add_layer_to_group_request.layer_id)


@router.post("/api/experiments/update_experiment_group_name", status_code=200)
async def update_experiment_group_name(update_name_request: UpdateNameRequest):
    '''
    API Request to update an experiment_group Name
    '''
    db_experiment_group = crud.read_experiment_db_group_by_uid(
        update_name_request.id)
    db_experiment_group.update_name(update_name_request.new_name)


@router.post("/api/experiments/update_experiment_group_hint", status_code=200)
async def update_experiment_group_hint(update_hint_request: UpdateHintRequest):
    '''
    API Request to update an experiment Hint
    '''
    db_experiment_group = crud.read_experiment_db_group_by_uid(
        update_hint_request.id)
    db_experiment_group.update_hint(update_hint_request.new_hint)


@router.post("/api/experiments/update_experiment_group_description", status_code=200)
async def update_experiment_group_description(update_description_request: UpdateDescriptionRequest):
    '''
    API Request to update an experiment description
    '''
    db_experiment_group = crud.read_experiment_db_group_by_uid(
        update_description_request.id)
    db_experiment_group.update_description(
        update_description_request.new_description)


@router.post("/api/experiments/update_experiment_group_images", status_code=200)
async def update_experiment_group_images(update_experiment_group_images_request: UpdateExperimentGroupImagesRequest):
    '''
    API Request to update images of an experiment group
    '''
    db_experiment_group = crud.read_experiment_db_group_by_uid(
        update_experiment_group_images_request.group_id)
    current_images = [image.uid for image in db_experiment_group.images]
    image_id_list = [
        _id for _id in update_experiment_group_images_request.image_id_list if _id not in current_images]
    db_experiment_group.update_images(image_id_list)


@router.post("/api/experiments/delete_image_from_experiment_group", status_code=200)
async def delete_image_from_experiment_group(delete_image_from_experiment_group_request: DeleteImageFromExperimentGroupRequest):
    '''
    API Request to update images of an experiment group
    '''
    db_experiment_group = crud.read_experiment_db_group_by_uid(
        delete_image_from_experiment_group_request.group_id)
    db_experiment_group.remove_image_by_uid(
        delete_image_from_experiment_group_request.image_id)


@router.post("/api/experiments/export_experiment", status_code=201)
async def export_experiment(export_experiment_request: ExportExperimentRequest):
    '''
    API Request to export an experiment

    export_experiment_request.export_request must include:
        export_types: dict
        images: bool
        masks: bool
        rois: bool
        rescaled: bool
        x_dim: int
        y_dim: int
    '''
    print(export_experiment_request)
    int_experiment = crud.read_experiment_by_uid(
        export_experiment_request.experiment_id).to_int_class()

    int_experiment.export_experiment(export_experiment_request.export_request)


@router.get("/api/experiments/export_mistos_experiment/{experiment_id}", status_code=201)
async def export_mistos_experiment(experiment_id: str):
    '''
    API request to export a mistos experiment to the export folder
    '''
    path = utils_export.export_mistos_experiment(int(experiment_id)).as_posix()
    return {"path": path}


@router.post("/api/experiments/import_mistos_experiment", status_code=201)
async def import_mistos_experiment(read_from_path_request: ReadFromPathRequest, response: Response):
    ''' 
    API Request to import an mistos image from a filepath.
    Included Layers and measurements will also be imported.
    '''
    path = pathlib.Path(read_from_path_request.path)
    if path.exists():
        path = path.as_posix()
    utils_import.import_mistos_experiment(path)
