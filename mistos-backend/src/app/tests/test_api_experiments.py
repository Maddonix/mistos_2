# import json
# import pathlib
# from app.api.com import api_images
# from app.tests.constants import *
# from app import crud
# from app.api.classes import IntImageResultLayer
# import numpy as np

# # setup: get some images with layers
# n_experiment_groups = 3


# def test_experiments_setup(test_app_simple):
#     for path in image_paths:
#         print(path.resolve())
#         print(f"Exists? {path.exists()}")
#         response = test_app_simple.post(
#             "/api/images/read_from_path", headers={"Content-Type": "application/json"},
#             json={
#                 "path": path.as_posix()
#             })
#         assert response.status_code == 201

#     response = test_app_simple.get(
#         "/api/images/fetch_all")
#     list_of_image_dicts = response.json()
#     assert response.status_code == 200

#     for image_dict in list_of_image_dicts:
#         uid = image_dict["uid"]
#         int_image = crud.read_image_by_uid(uid)
#         label_array = get_test_label_array(int_image)

#         int_result_layer = IntImageResultLayer(
#             uid=-1,
#             name=f"test_layer_{int_image.name}",
#             image_id=int_image.uid,
#             layer_type="labels", data=label_array
#         )
#         int_result_layer.on_init()
#         int_image.refresh_from_db()
#         int_image.measure_mask_in_image(
#             int_result_layer.uid)


# def test_create_new_experiment_with_groups(test_app_simple):
#     response = test_app_simple.post(
#         "/api/experiments/create_new_experiment", headers={"Content-Type": "application/json"},
#         json={
#             "experiment": com_experiment.dict()
#         })
#     assert response.status_code == 201
#     response = test_app_simple.get("api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     response = test_app_simple.get("api/experiments/fetch_all")
#     assert response.status_code == 200
#     # New Group
#     for i in range(n_experiment_groups):
#         response = test_app_simple.post(
#             "/api/experiments/new_group_by_id", headers={"Content-Type": "application/json"},
#             json={
#                 "experiment_id": 1
#             })
#         assert response.status_code == 201
#     response = test_app_simple.get("api/experiments/fetch_by_id/1")
#     experiment_dict = response.json()
#     assert len(experiment_dict["experimentGroups"]) == n_experiment_groups


# def test_update_experiment(test_app_simple):
#     response = test_app_simple.post(
#         "/api/experiments/update_experiment_name", headers={"Content-Type": "application/json"},
#         json={
#             "id": 1,
#             "new_name": "test name!"
#         })
#     assert response.status_code == 200
#     response = test_app_simple.post(
#         "/api/experiments/update_experiment_hint", headers={"Content-Type": "application/json"},
#         json={
#             "id": 1,
#             "new_hint": "test hint!"
#         })
#     assert response.status_code == 200
#     response = test_app_simple.post(
#         "/api/experiments/update_experiment_description", headers={"Content-Type": "application/json"},
#         json={
#             "id": 1,
#             "new_description": "test description!"
#         })
#     assert response.status_code == 200
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_dict = response.json()
#     assert experiment_dict["name"] == "test name!"
#     assert experiment_dict["hint"] == "test hint!"
#     assert experiment_dict["description"] == "test description!"


# def test_update_experiment_group(test_app_simple):
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_groups = response.json()["experimentGroups"]
#     for group_dict in experiment_groups:
#         group_id = group_dict["uid"]
#         # Update name
#         response = test_app_simple.post(
#             "/api/experiments/update_experiment_group_name", headers={"Content-Type": "application/json"},
#             json={
#                 "id": group_id,
#                 "new_name": "test name!"
#             })
#         assert response.status_code == 200
#         # Update hint
#         response = test_app_simple.post(
#             "/api/experiments/update_experiment_group_hint", headers={"Content-Type": "application/json"},
#             json={
#                 "id": group_id,
#                 "new_hint": "test hint!"
#             })
#         assert response.status_code == 200
#         # update description
#         response = test_app_simple.post(
#             "/api/experiments/update_experiment_group_description", headers={"Content-Type": "application/json"},
#             json={
#                 "id": group_id,
#                 "new_description": "test description!"
#             })
#         assert response.status_code == 200

#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_groups = response.json()["experimentGroups"]
#     for group_dict in experiment_groups:
#         assert group_dict["name"] == "test name!"
#         assert group_dict["hint"] == "test hint!"
#         assert group_dict["description"] == "test description!"


# def test_add_image_to_experiment_group(test_app_simple):
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_dict = response.json()
#     # add images
#     response = test_app_simple.get(
#         "/api/images/fetch_all")
#     list_of_image_dicts = response.json()
#     assert response.status_code == 200
#     image_ids = [image_dict["uid"] for image_dict in list_of_image_dicts]
#     for experiment_group_dict in experiment_dict["experimentGroups"]:
#         experiment_group_id = experiment_group_dict["uid"]
#         response = test_app_simple.post(
#             "/api/experiments/update_experiment_group_images", headers={"Content-Type": "application/json"},
#             json={"group_id": experiment_group_id, "image_id_list": image_ids})
#         assert response.status_code == 200
#     # add layers
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_dict = response.json()
#     for experiment_group_dict in experiment_dict["experimentGroups"]:
#         experiment_group_id = experiment_group_dict["uid"]
#         for image_dict in list_of_image_dicts:
#             for layer_dict in image_dict["imageResultLayers"]:
#                 layer_id = layer_dict["uid"]
#                 response = test_app_simple.post(
#                     "/api/experiments/add_result_layer_to_group", headers={"Content-Type": "application/json"},
#                     json={"group_id": experiment_group_id, "layer_id": layer_id})
#                 assert response.status_code == 200


# def test_remove_image_from_experiment_group(test_app_simple):
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_dict = response.json()
#     experiment_group_dict = experiment_dict["experimentGroups"][0]
#     group_id = experiment_group_dict["uid"]
#     result_layer_id = experiment_group_dict["resultLayerIds"][0]
#     db_result_layer = crud.read_result_layer_by_uid(result_layer_id)
#     image_id = db_result_layer.image_id
#     response = test_app_simple.post(
#         "/api/experiments/delete_image_from_experiment_group", headers={"Content-Type": "application/json"},
#         json={"group_id": group_id, "image_id": image_id})
#     assert response.status_code == 200
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_dict = response.json()
#     experiment_group_dict = experiment_dict["experimentGroups"][0]
#     assert result_layer_id not in experiment_group_dict["resultLayerIds"]
#     response = test_app_simple.post(
#         "/api/experiments/delete_group_by_id", headers={"Content-Type": "application/json"},
#         json={"experiment_id": experiment_dict["uid"], "group_id": group_id})
#     assert response.status_code == 200
#     response = test_app_simple.get(
#         "/api/experiments/fetch_by_id/1")
#     assert response.status_code == 200
#     experiment_dict = response.json()
#     group_id_list = [_["uid"] for _ in experiment_dict["experimentGroups"]]
#     assert group_id not in group_id_list


# def test_export_experiment(test_app_simple):
#     for export_experiment_request in export_experiment_requests:
#         print(export_experiment_request)
#         response = test_app_simple.post(
#             "/api/experiments/export_experiment", headers={"Content-Type": "application/json"},
#             json={"experiment_id": 1, "export_request": export_experiment_request})
#         assert response.status_code == 201


# def test_export_import_mistos_experiment(test_app_simple):
#     response = test_app_simple.get(
#         "/api/experiments/export_mistos_experiment/1")
#     assert response.status_code == 201
#     path = response.json()["path"]
#     response = test_app_simple.post(
#         "/api/experiments/import_mistos_experiment", headers={"Content-Type": "application/json"},
#         json={"path": path})
#     assert response.status_code == 201


# # Cleanup
# def test_delete_experiment(test_app_simple):
#     response = test_app_simple.get(
#         "/api/experiments/fetch_all")
#     list_of_experiment_dicts = response.json()
#     assert response.status_code == 200
#     for experiment_dict in list_of_experiment_dicts:
#         print(experiment_dict)
#         response = test_app_simple.post(
#             "/api/experiments/delete_by_id", headers={"Content-Type": "application/json"},
#             json={
#                 "experiment_id": experiment_dict["uid"]
#             })
#         assert response.status_code == 200


# def test_delete_images(test_app_simple):
#     response = test_app_simple.get(
#         "/api/images/fetch_all")
#     list_of_image_dicts = response.json()
#     assert response.status_code == 200

#     for image_dict in list_of_image_dicts:
#         response = test_app_simple.post(
#             "/api/images/delete_by_id", headers={"Content-Type": "application/json"},
#             json={
#                 "id": image_dict["uid"]
#             })
#         assert response.status_code == 200

#     response = test_app_simple.get(
#         "/api/images/fetch_all")
#     assert response.status_code == 200
#     assert len(response.json()) == 0
