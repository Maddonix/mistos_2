# pylint:disable=no-name-in-module, import-error
from fastapi import APIRouter
import app.api.classes_internal as c_int
from app.api import utils_deepflash
from fastapi import APIRouter
import pathlib
from app import crud
from app.api.com.api_request_models import EstimateGroundTruthRequest, ReadFromPathRequest, PredictImagesRequest

router = APIRouter()


@router.post("/api/deepflash/estimate_ground_truth", status_code=200)
async def estimate_ground_truth(estimate_ground_truth_request: EstimateGroundTruthRequest):
    '''
    API Request to generate ground truth labels for image.
    images label dict has following structure: {
        f"{image_id}_{expert_number}": label_uid
    }
    '''
    _images_label_dict = estimate_ground_truth_request.images_label_dict
    image_ids = []
    experts = []
    label_ids = []
    images_label_dict = {}
    for key, value in _images_label_dict.items():
        _key = key.split("_")
        image_ids.append(int(_key[0]))
        experts.append(int(_key[1]))
        label_ids.append(int(value))

    for image_id in image_ids:
        images_label_dict[image_id] = []

    for i, label_id in enumerate(label_ids):
        images_label_dict[image_ids[i]].append(label_id)

    for image_id, label_id_list in images_label_dict.items():
        int_image = crud.read_image_by_uid(image_id)
        int_image.calculate_ground_truth_layer(label_id_list, suffix="")


@router.post("/api/deepflash/read_from_path", status_code=201)
async def upload_deepflash_model(read_from_path_request: ReadFromPathRequest):
    ''' 
    API Request to read and import a Deepflash model. Expects Folder containing models for an ensemble.
    '''
    path = pathlib.Path(read_from_path_request.path)
    name = path.as_posix().split("/")[-1]
    files = [_ for _ in path.glob("*")]

    c_int_classifier_deepflash = c_int.IntClassifier(
        uid=-1,
        name=name,
        clf_type="deepflash_model",
        tags=set(),
        classifier=files,
        params={},
        metrics={}
    )
    c_int_classifier_deepflash.on_init()

    return {"Result": "OK"}


@router.post("/api/deepflash/predict_images", status_code=200)
async def predict_images(predict_images_request: PredictImagesRequest):
    '''
    API Request to read a deepflash model, apply it to a list of images and save the results as image layers
    '''
    classifier_id = predict_images_request.classifier_id
    image_ids = predict_images_request.image_ids
    use_tta = predict_images_request.use_tta

    utils_deepflash.predict_image_list(classifier_id, image_ids, use_tta)


@router.post("/api/deepflash/predict_images_3d", status_code=200)
async def predict_images_3d(predict_images_request: PredictImagesRequest):
    '''
    API Request to read a deepflash model, apply it to a list of images and save the results as image layers
    '''
    classifier_id = predict_images_request.classifier_id
    image_ids = predict_images_request.image_ids
    use_tta = predict_images_request.use_tta
    channel = predict_images_request.channel

    utils_deepflash.predict_image_list(
        classifier_id, image_ids, use_tta, channel=channel, separate_z_slices=True)


# TO DO: Adapt to upload and save folder
# @router.post("/api/deepflash/upload_model", status_code = 201)
# async def upload_deepflash_model(file:UploadFile = File(...)):
#     '''
#     API Request to upload a deepflash model.
#     '''
#     path = utils_paths.make_tmp_file_path(file.filename)
#     path = utils_paths.fileserver.joinpath(path).as_posix()
#     async with aiofiles.open(path, 'wb') as out_file:
#         while content := await file.read(1024):  # async read chunk
#             await print(type(content))
#             # await out_file.write(content)  # async write chunk

#     c_int_classifier_deepflash = c_int.IntClassifier(
#         uid= -1,
#         name= file.filename.split(".")[0],
#         clf_type= "deepflash_model",
#         tags=set(),
#         params = {},
#         metrics = {}
#     )
#     c_int_classifier_deepflash.on_init()

#     fsr.delete_file(path)

#     return {"Result": "OK"}
