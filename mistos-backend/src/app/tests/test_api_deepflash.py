import pathlib
from app.tests.constants import *
from app import crud
from app.api.classes import IntImageResultLayer
import numpy as np

n_test_result_layers = 3
image_label_dict = {}


def test_setup(test_app_simple):

    for path in image_paths:
        print(path.resolve())
        print(f"Exists? {path.exists()}")
        response = test_app_simple.post(
            "/api/images/read_from_path", headers={"Content-Type": "application/json"},
            json={
                "path": path.as_posix()
            })
        assert response.status_code == 201

    response = test_app_simple.get(
        "/api/images/fetch_all")
    list_of_image_dicts = response.json()
    assert response.status_code == 200

    for image_dict in list_of_image_dicts:
        uid = image_dict["uid"]
        int_image = crud.read_image_by_uid(uid)
        for i in range(n_test_result_layers):
            label_array = get_test_label_array(int_image)

            int_result_layer = IntImageResultLayer(
                uid=-1,
                name=f"test_layer_{int_image.name}",
                image_id=int_image.uid,
                layer_type="labels", data=label_array
            )
            int_result_layer.on_init()
            int_image.refresh_from_db()
            int_image.measure_mask_in_image(
                int_result_layer.uid)
            image_label_dict[f"{uid}_{i}"] = int_result_layer.uid


def test_estimate_ground_truth(test_app_simple):
    response = test_app_simple.post(
        "/api/deepflash/estimate_ground_truth", headers={"Content-Type": "application/json"},
        json={
            "images_label_dict": image_label_dict
        })
    assert response.status_code == 201


def test_read_deepflash_and_apply_model_from_path(test_app_simple):
    response = test_app_simple.post(
        "/api/deepflash/read_from_path", headers={"Content-Type": "application/json"},
        json={
            "path": deepflash_model_folder.as_posix()
        })
    assert response.status_code == 201
    classifier_id = response.json()["uid"]
    response = test_app_simple.get("/api/classifier/fetch_all")
    assert response.status_code == 200
    response = test_app_simple.get(
        f"/api/classifier/fetch_df_by_id/{classifier_id}")
    assert response.status_code == 200
    image_ids = [i+1 for i in range(n_test_images)]
    # 2d (z stacks will be max z projected)
    response = test_app_simple.post(
        "/api/deepflash/predict_images", headers={"Content-Type": "application/json"},
        json={
            "classifier_id": classifier_id,
            "channel": 0,
            "image_ids": image_ids,
            "use_tta": False
        })
    assert response.status_code == 201
    # 3d (z slices will be analysed seperately and layer mask is reconstructed)
    response = test_app_simple.post(
        "/api/deepflash/predict_images_3d", headers={"Content-Type": "application/json"},
        json={
            "classifier_id": classifier_id,
            "channel": 0,
            "image_ids": image_ids,
            "use_tta": False
        })
    assert response.status_code == 201

    # classifier_list = response.json


# Cleanup


def test_delete_classifiers(test_app_simple):
    response = test_app_simple.get(
        f"/api/classifier/fetch_all")
    assert response.status_code == 200
    list_of_classifier_dicts = response.json()
    for com_clf in list_of_classifier_dicts:
        clf_id = com_clf["uid"]
        assert clf_id > 0
        print(list_of_classifier_dicts)

        response = test_app_simple.post(
            "/api/classifier/delete_by_id", headers={"Content-Type": "application/json"},
            json={
                "id": clf_id
            })
        assert response.status_code == 200


def test_delete_experiment(test_app_simple):
    response = test_app_simple.get(
        "/api/experiments/fetch_all")
    list_of_experiment_dicts = response.json()
    assert response.status_code == 200
    for experiment_dict in list_of_experiment_dicts:
        print(experiment_dict)
        response = test_app_simple.post(
            "/api/experiments/delete_by_id", headers={"Content-Type": "application/json"},
            json={
                "experiment_id": experiment_dict["uid"]
            })
        assert response.status_code == 200


def test_delete_images(test_app_simple):
    response = test_app_simple.get(
        "/api/images/fetch_all")
    list_of_image_dicts = response.json()
    assert response.status_code == 200

    for image_dict in list_of_image_dicts:
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
