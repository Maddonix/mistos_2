# import json
# from starlette.testclient import TestClient
# import pathlib

# test_images_folder = pathlib.Path("../../../../tutorial/Demo Experiment 1")

# image_paths = [
#     test_images_folder.joinpath("1.png"),
#     test_images_folder.joinpath("2.png"),
#     test_images_folder.joinpath("3.png"),    
#     test_images_folder.joinpath("4.png"),    
#     test_images_folder.joinpath("image_series.czi"),    
#     test_images_folder.joinpath("multichannel_z_stack.oib")
# ]

# def test_import_file_by_filepath(test_app_simple):
#     """
#     Test the http-status code of the 'POST /api/images' endpoint.

#     Parameters:
#         - test_app_simple(starlette.testclient.TestClient): The FastAPI-TestClient used for testing.
#     """
#     response = test_app_simple.post(
#         "api/patient", headers={"Content-Type": "application/json"}, json={"firstName": "Harry", "familyName": "Potter", "birthday": "1980-07-31", "staffId": 1})
#     print(response.json())
#     assert response.status_code == 201