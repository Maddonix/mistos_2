# pylint:disable=no-name-in-module, import-error
import aiofiles
import time
from fastapi import APIRouter, File, UploadFile, Response, status
import app.api.utils_com as utils_com
from app.api import classes_internal as c_int
from app import crud, fileserver_requests
from app.api import napari_viewer
from fastapi.responses import JSONResponse
from app.api import utils_import, utils_paths, utils_export
import numpy as np
import zarr
import pathlib

import asyncio

from app.api.com.api_request_models import (ViewImageRequest, DeleteRequest, UpdateHintRequest, UpdateChannelNamesRequest, UpdateNameRequest,
ReadFromPathRequest)

router = APIRouter()

# GET
@router.get("/api/images/fetch_all", status_code=200)
async def fetch_all_images():
    """
    API request to return a list of all images
    """
    image_list = utils_com.get_com_image_list()
    return image_list

@router.get("/api/images/fetch_by_id/{image_uid}", status_code=200)
async def fetch_image_by_id(
    image_uid:str
):
    """
    API request to return a single image by uid
    """
    image_uid = int(image_uid)
    image = utils_com.get_com_image_by_uid(image_uid)
    return image

@router.get("/api/images/fetch_thumbnail_path/{image_uid}")
async def fetch_thumbnail_path(image_uid:str):
    '''
    API request to return the path of an images thumbnail
    '''
    path = utils_paths.make_thumbnail_path(int(image_uid))
    path = "http://" + utils_paths.static_fileserver + path
    return {"path": path}
    # return utils_paths.fileserver.joinpath()

@router.get("/api/images/export_mistos_image/{image_uid}")
async def export_image(image_uid:str):
    '''
    API request to export an image to the export folder
    '''
    utils_export.export_mistos_image(int(image_uid))

# POST
@router.post("/api/images/view_by_id", status_code=200)
async def view_image_by_id(post: ViewImageRequest):
    '''
    API expects a json of format {
        "image_id": int,
        "display_result_layers": bool, 
        "display_background_layers":bool}.
    It reads the image by id from the database and opens it with the napari viewer.

    To-Do: Make Asynchronous?
    '''
    c_int_image = crud.read_image_by_uid(post.image_id)
    napari_viewer.view(
        c_int_image,
        post.display_result_layers,
        post.display_background_layers
    )
    return JSONResponse(content = {
        "imageId": c_int_image.uid,
        "imageClosed": True
    })

@router.post("/api/images/upload", status_code = 201)
async def upload_image(file:UploadFile = File(...)):
    ''' 
    API Request to upload an image.
    '''
    path = utils_paths.make_tmp_file_path(file.filename)
    path = utils_paths.fileserver.joinpath(path).as_posix()
    async with aiofiles.open(path, 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk


    image_list, metadata_dict, metadata_OMEXML = utils_import.read_image_file(path)
    print(metadata_dict)
    for image, i in image_list:
            img_zarr = zarr.creation.array(image)
            int_image = c_int.IntImage(
                uid = -1,
                series_index = i,
                name = metadata_dict["original_filename"],#.replace("\#", "_"),
                metadata = metadata_dict, # This is not the finished metadata!
                data = img_zarr,
                metadata_omexml = metadata_OMEXML
                )
            int_image.on_init()
            
    fileserver_requests.delete_file(path)

    return {"Result": "OK"}

@router.post("/api/images/upload_max_z_projection", status_code = 201)
async def upload_image_max_z_projection(file:UploadFile = File(...)):
    ''' 
    API Request to upload an image and save its max z projection.
    '''
    path = utils_paths.make_tmp_file_path(file.filename)
    path = utils_paths.fileserver.joinpath(path).as_posix()
    async with aiofiles.open(path, 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk


    image_list, metadata_dict, metadata_OMEXML = utils_import.read_image_file(path)
    for image, i in image_list:
            img_zarr = zarr.creation.array(image)
            img_zarr = np.array(img_zarr).max(axis = 0)
            img_zarr = img_zarr[np.newaxis, ...]

            int_image = c_int.IntImage(
                uid = -1,
                series_index = i,
                name = metadata_dict["original_filename"],
                metadata = metadata_dict, # This is not the finished metadata!
                data = img_zarr,
                metadata_omexml = metadata_OMEXML
                )
            int_image.on_init()
            
    fileserver_requests.delete_file(path)

    return {"Result": "OK"}
    # img = file.file

@router.post("/api/images/read_from_path", status_code = 201)
async def read_from_path(read_image_from_path_request: ReadFromPathRequest, response: Response):
    ''' 
    API Request to import an image from a filepath
    '''
    path = pathlib.Path(read_image_from_path_request.path)
    print(path)
    if path.exists():
        path = path.as_posix()
        image_list, metadata_dict, metadata_OMEXML = utils_import.read_image_file(path)
        for image, i in image_list:
                img_zarr = zarr.creation.array(image)

                int_image = c_int.IntImage(
                    uid = -1,
                    series_index = i,
                    name = metadata_dict["original_filename"],
                    metadata = metadata_dict, # This is not the finished metadata!
                    data = img_zarr,
                    metadata_omexml = metadata_OMEXML
                    )
                int_image.on_init()
        return {"Result": "OK"}

    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Result": "File not found"}

@router.post("/api/images/read_from_path_max_z_projection", status_code = 201)
async def read_from_path_max_z_projection(read_image_from_path_request: ReadFromPathRequest, response: Response):
    ''' 
    API Request to import an image as max-z-projection from a filepath
    '''
    path = pathlib.Path(read_image_from_path_request.path)
    if path.exists():
        path = path.as_posix()
        image_list, metadata_dict, metadata_OMEXML = utils_import.read_image_file(path)
        for image, i in image_list:
                img_zarr = zarr.creation.array(image)
                img_zarr = np.array(img_zarr).max(axis = 0)
                img_zarr = img_zarr[np.newaxis, ...]

                int_image = c_int.IntImage(
                    uid = -1,
                    series_index = i,
                    name = metadata_dict["original_filename"],
                    metadata = metadata_dict, # This is not the finished metadata!
                    data = img_zarr,
                    metadata_omexml = metadata_OMEXML
                    )
                int_image.on_init()
        return {"Result": "OK"}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Result": "File not found"}

@router.post("/api/images/import_mistos_image", status_code = 201)
async def import_mistos_image(read_from_path_request: ReadFromPathRequest, response: Response):
    ''' 
    API Request to import an mistos image from a filepath.
    Included Layers and measurements will also be imported.
    '''
    path = pathlib.Path(read_from_path_request.path)
    if path.exists():
        path = path.as_posix()
    utils_import.import_mistos_image(path, for_experiment = False)

@router.post("/api/images/update_image_hint", status_code = 200)
async def update_image_hint(update_hint_request: UpdateHintRequest):
    db_image = crud.read_db_image_by_uid(update_hint_request.id)
    db_image.update_hint(update_hint_request.new_hint)

@router.post("/api/images/update_image_channel_names", status_code = 200)
async def update_image_channel_names(update_channel_names_request: UpdateChannelNamesRequest):
    '''
    Queries for image, uses db_image to calls db_image.update_channel_names
    '''
    print(update_channel_names_request)
    db_image = crud.read_db_image_by_uid(update_channel_names_request.image_id)
    db_image.update_channel_names(update_channel_names_request.channel_names)

@router.post("/api/images/delete_by_id", status_code = 201)
async def delete_image(request: DeleteRequest):
    db_image = crud.read_db_image_by_uid(request.id)
    db_image.delete_from_system()

@router.post("/api/images/update_layer_name", status_code = 200)
async def update_layer_name(update_name_request: UpdateNameRequest):
    '''
    API Request to update layer name
    '''
    db_layer = crud.read_result_layer_by_uid(update_name_request.id)
    db_layer.update_name(update_name_request.new_name)

@router.post("/api/images/update_layer_hint", status_code = 200)
async def update_layer_hint(update_hint_request: UpdateHintRequest):
    '''
    API Request to update layer name
    '''
    db_layer = crud.read_result_layer_by_uid(update_hint_request.id)
    db_layer.update_hint(update_hint_request.new_hint)

@router.post("/api/images/delete_layer", status_code = 200)
async def delete_layer(delete_request: DeleteRequest):
    '''
    API Request to delete Layer.
    '''
    db_layer = crud.read_result_layer_by_uid(delete_request.id)
    db_image = crud.read_db_image_by_uid(db_layer.image_id)
    db_layer.delete()
    db_image.set_bg_false()
    
