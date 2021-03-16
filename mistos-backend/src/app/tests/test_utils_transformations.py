from app.tests.constants import (
    image_paths, get_test_label_array, 
    fetch_all_images, delete_all_images, 
    read_image_from_path,make_result_layer)
from app.api.utils_transformations import (rescale_image, z_project)
from app.api.classes import IntImageResultLayer
from app import crud
import numpy as np

def test_setup_import_images(test_app_simple):
    for path in image_paths:
        print(path.resolve())
        print(f"Exists? {path.exists()}")
        response = read_image_from_path(test_app_simple, path)
        assert response.status_code == 201

    response = fetch_all_images(test_app_simple)
    list_of_image_dicts = response.json()
    assert response.status_code == 200

    for image_dict in list_of_image_dicts:
        uid = image_dict["uid"]
        int_image = crud.read_image_by_uid(uid)
        label_array = get_test_label_array(int_image)

        int_image, int_result_layer = make_result_layer(int_image, label_array)

def test_rescale_image(test_app_simple):
    list_of_image_dicts = fetch_all_images(test_app_simple).json()
    image_list = [crud.read_image_by_uid(img_dict["uid"]) for img_dict in list_of_image_dicts]
    for int_image in image_list:
        shape = int_image.data.shape
        x_dim = 1000
        y_dim = 1000
        reshaped_array = rescale_image(int_image.data, x_dim = x_dim, y_dim = y_dim)
        assert reshaped_array.shape == (shape[0], shape[1], y_dim, x_dim)
        x_dim = 100
        y_dim = 100
        reshaped_array = rescale_image(int_image.data, x_dim = x_dim, y_dim = y_dim)
        assert reshaped_array.shape == (shape[0], shape[1], y_dim, x_dim)
        for result_layer in int_image.image_result_layers:
            result_layer_array = result_layer.data[:, np.newaxis, ...]
            shape = result_layer_array.shape
            x_dim = 1000
            y_dim = 1000
            reshaped_array = rescale_image(result_layer_array.data, x_dim = x_dim, y_dim = y_dim)
            assert reshaped_array.shape == (shape[0], shape[1], y_dim, x_dim)
            x_dim = 100
            y_dim = 100
            reshaped_array = rescale_image(result_layer_array.data, x_dim = x_dim, y_dim = y_dim)
            assert reshaped_array.shape == (shape[0], shape[1], y_dim, x_dim)

def test_z_project(test_app_simple):
    list_of_image_dicts = fetch_all_images(test_app_simple).json()
    image_list = [crud.read_image_by_uid(img_dict["uid"]) for img_dict in list_of_image_dicts]
    for int_image in image_list:
        shape = int_image.data.shape
        max_z_projection = z_project(int_image.data)
        assert max_z_projection.shape == (1, shape[1], shape[2], shape[3])
        for result_layer in int_image.image_result_layers:
            shape = result_layer.data.shape
            max_z_projection = z_project(result_layer.data)
            assert max_z_projection.shape == (1, shape[1], shape[2])
            
def test_cleanup(test_app_simple):
    delete_all_images(test_app_simple)
    response = fetch_all_images(test_app_simple)
    assert len(response.json()) == 0
