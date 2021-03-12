import json
import pathlib
from app.api.com import api_images
from app.tests.constants import *
from app import crud
from app.api.classes import IntImageResultLayer
import numpy as np


# test_app_simple is provided by conftest.test_app_simple


def test_import_images_from_path(test_app_simple):
    '''
    to be done:
        - incorrect filepaths
        - broken file
    '''
    for path in image_paths:
        print(path.resolve())
        print(f"Exists? {path.exists()}")
        response = test_app_simple.post(
            "/api/images/read_from_path", headers={"Content-Type": "application/json"},
            json={
                "path": path.as_posix()
            })
        print(response)
        assert response.status_code == 201


def test_import_max_z_images_from_path(test_app_simple):
    '''
    to be done:
        - incorrect filepaths
        - broken file
    '''
    for path in image_paths:
        response = test_app_simple.post(
            "/api/images/read_from_path_max_z_projection", headers={"Content-Type": "application/json"},
            json={
                "path": path.as_posix()
            })
        assert response.status_code == 201


def test_upload_image(test_app_simple):
    pass


def test_upload_image_max_z(test_app_simple):
    pass


def test_update_image_hint(test_app_simple):
    uid = 1
    for hint in test_strings[:2]:
        response = test_app_simple.post(
            "/api/images/update_image_hint", headers={"Content-Type": "application/json"},
            json={
                "id": uid,
                "new_hint": hint
            })
        if type(hint) == str:
            assert response.status_code == 200
        else:
            pass
        response = test_app_simple.get(f"api/images/fetch_by_id/{uid}")
        com_image_json = response.json()
        assert com_image_json["hint"] == hint


def test_update_image_channel_names(test_app_simple):
    for i, channel_names in enumerate(channel_names_list):
        uid = i+1
        response = test_app_simple.post(
            "/api/images/update_image_channel_names", headers={"Content-Type": "application/json"},
            json={
                "image_id": uid,
                "channel_names": channel_names
            })
        assert response.status_code == 200
        response = test_app_simple.get(f"api/images/fetch_by_id/{uid}")
        com_image_json = response.json()
        assert com_image_json["metadata"]["custom_channel_names"] == channel_names


def test_fetch_thumbnail_path(test_app_simple):
    # To Do: Test if thumbnail exists!
    for i in range(len(image_paths)):
        uid = i+1
        response = test_app_simple.get(
            f"api/images/fetch_thumbnail_path/{uid}")
        path = response.json()["path"]
        assert response.status_code == 200


def test_export_import_mistos_image(test_app_simple):
    for i in range(len(image_paths)):
        uid = i+1
        response = test_app_simple.get(
            f"api/images/export_mistos_image/{uid}")
        assert response.status_code == 201
        path = response.json()["path"]
        assert pathlib.Path(path).exists()
        response = test_app_simple.post(
            "/api/images/import_mistos_image", headers={"Content-Type": "application/json"},
            json={
                "path": path
            })
        assert response.status_code == 201


def test_view_image_by_id(test_app_simple):
    pass


def test_layer(test_app_simple):
    response = test_app_simple.get(
        "/api/images/fetch_all")
    list_of_image_dicts = response.json()
    assert response.status_code == 200

    for image_dict in list_of_image_dicts:
        uid = image_dict["uid"]
        int_image = crud.read_image_by_uid(uid)
        label_array = get_test_label_array(int_image)

        int_result_layer = IntImageResultLayer(
            uid=-1,
            name=f"test_layer_{int_image.name}",
            image_id=int_image.uid,
            layer_type="labels", data=label_array
        )
        int_result_layer.on_init()
        db_result_layer = crud.read_result_layer_by_uid(int_result_layer.uid)

        response = test_app_simple.post(
            "/api/images/update_layer_name", headers={"Content-Type": "application/json"},
            json={
                "id": int_result_layer.uid,
                "new_name": "test_name!"
            })
        assert response.status_code == 200
        response = test_app_simple.post(
            "/api/images/update_layer_hint", headers={"Content-Type": "application/json"},
            json={
                "id": int_result_layer.uid,
                "new_hint": "test_hint!"
            })
        assert response.status_code == 200
        db_result_layer = crud.read_result_layer_by_uid(int_result_layer.uid)
        assert db_result_layer.name == "test_name!"
        assert db_result_layer.hint == "test_hint!"

        response = test_app_simple.post(
            "/api/images/delete_layer", headers={"Content-Type": "application/json"},
            json={
                "id": int_result_layer.uid
            })
        assert response.status_code == 200

        result_layer_list = crud.read_result_layers_of_image_uid(uid)
        assert len(result_layer_list) == 0


def test_import_image_layers(test_app_simple):
    response = test_app_simple.get(
        "/api/images/fetch_all")
    list_of_image_dicts = response.json()[:n_test_images]
    assert response.status_code == 200
    # mask from image
    for i, image_dict in enumerate(list_of_image_dicts):
        for mask_path in mask_paths[i]:
            response = test_app_simple.post(
                f"/api/images/import_layer_to_image/{image_dict['uid']}", headers={"Content-Type": "application/json"},
                json={
                    "path": mask_path.as_posix()
                })
            assert response.status_code == 201
    # mask from roi
    for i, image_dict in enumerate(list_of_image_dicts):
        for roi_path in roi_paths:
            response = test_app_simple.post(
                f"/api/images/import_layer_to_image/{image_dict['uid']}", headers={"Content-Type": "application/json"},
                json={
                    "path": roi_path.as_posix()
                })
            assert response.status_code == 201


def test_delete_images(test_app_simple):
    '''
    to do:
    check if layers are deleted if images are deleted by adding more layers than deleting in tests above than
    '''
    response = test_app_simple.get(
        "/api/images/fetch_all")
    list_of_image_dicts = response.json()
    assert response.status_code == 200

    for image_dict in list_of_image_dicts:
        # Test if image was initialized
        assert image_dict["uid"] > 0
        # Test if all channels are named
        assert len(image_dict["metadata"]["custom_channel_names"]
                   ) == image_dict["metadata"]["n_channels"]

        # Delete image
        response = test_app_simple.post(
            "/api/images/delete_by_id", headers={"Content-Type": "application/json"},
            json={
                "id": image_dict["uid"]
            })
        assert response.status_code == 200

    response = test_app_simple.get(
        "/api/images/fetch_all")
    assert response.status_code == 200
    assert len(response.json()) == 0
