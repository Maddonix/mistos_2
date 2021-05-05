import pathlib
import numpy as np
from app.api.classes import *
from app.api.classes_com import *
import skimage.draw

test_images_folder = pathlib.Path("../../tutorial/Demo Experiment 1")
deepflash_model_folder = pathlib.Path(
    r"F:\Google Drive\AG_Rittner\Masterarbeit\deepflash_model_18")

# Varbiables for testing
n_test_images = 2
image_paths = [
    test_images_folder.joinpath("1.png"),
    test_images_folder.joinpath("multichannel_z_stack.oib"),
    test_images_folder.joinpath("image_series.czi")
]
image_paths = image_paths[:n_test_images]

test_masks_rois_folder = pathlib.Path("app/tests/test_masks")
roi_paths = [
    test_masks_rois_folder.joinpath("1_rois.zip"),
    test_masks_rois_folder.joinpath("2_rois.zip"),
    None
]
roi_paths = roi_paths[:n_test_images]

mask_paths = [
    [
        test_masks_rois_folder.joinpath("1.png"),
        test_masks_rois_folder.joinpath("1.tiff"),
        test_masks_rois_folder.joinpath("1_max_z.tiff"),
    ], [
        test_masks_rois_folder.joinpath("1.png"),
        test_masks_rois_folder.joinpath("1.tiff"),
        test_masks_rois_folder.joinpath("1_max_z.tiff"),
    ],
    [None]
]
mask_paths = mask_paths[:n_test_images]

channel_names_list = [
    [""],
    ["c01", "c02", "c03"],
    [""]
]
channel_names_list = channel_names_list[:n_test_images]

test_strings = [
    "",
    "test"
    "test hint!123%?ß",
    1,
    None]

incorrect_path = pathlib.Path("")

com_experiment = ComExperiment(
    uid=-1,
    name="Test experiment!",
    hint="asd",
    description="asd",
    tags=[]
)

export_experiment_requests = [
    # only results xlsx
    {
        "images": False,
        "masks": False,
        "rois": False,
        "rescaled": False,
        "z_projection": False,
        "masks_binary": False,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 1024,  # not used if rescaled is false
        "y_dim": 1024,
        "export_deepflash": False
    },
    # + images
    {
        "images": True,
        "masks": False,
        "rois": False,
        "rescaled": False,
        "z_projection": False,
        "masks_binary": False,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 1024,  # not used if rescaled is false
        "y_dim": 1024,
        "export_deepflash": False
    },
    # + masks
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": False,
        "z_projection": False,
        "masks_binary": False,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 1024,  # not used if rescaled is false
        "y_dim": 1024,
        "export_deepflash": False
    },
    # + rescaled
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": True,
        "z_projection": False,
        "masks_binary": False,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 700,  # not used if rescaled is false
        "y_dim": 1200,
        "export_deepflash": False
    },
    # max_z instead of z-stacks images and masks
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": True,
        "z_projection": True,
        "masks_binary": False,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 1200,  # not used if rescaled is false
        "y_dim": 700,
        "export_deepflash": False
    },  # Masks as binary
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": True,
        "z_projection": True,
        "masks_binary": True,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 1400,  # not used if rescaled is false
        "y_dim": 1400,
        "export_deepflash": False
    },
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": True,
        "z_projection": False,
        "masks_binary": True,
        "masks_png": False,
        "images_single_channel": -1,  # Means no
        "x_dim": 800,  # not used if rescaled is false
        "y_dim": 800,
        "export_deepflash": False
    },
    # Single channel
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": True,
        "z_projection": False,
        "masks_binary": True,
        "masks_png": False,
        "images_single_channel": 0,  # Means no
        "x_dim": 800,  # not used if rescaled is false
        "y_dim": 800,
        "export_deepflash": False
    },
    # Masks as png
    {
        "images": True,
        "masks": True,
        "rois": False,
        "rescaled": True,
        "z_projection": False,  # Should be performed automatically
        "masks_binary": False,  # Should be performed automatically
        "masks_png": True,
        "images_single_channel": -1,  # Means no
        "x_dim": 800,  # not used if rescaled is false
        "y_dim": 800,
        "export_deepflash": False
    },
    # png with single channel selection
    {
        "images": True,
        "masks": True,
        "rois": True,
        "rescaled": True,
        "z_projection": False,  # Should be performed automatically
        "masks_binary": False,  # Should be performed automatically
        "masks_png": True,
        "images_single_channel": 0,
        "x_dim": 800,  # not used if rescaled is false
        "y_dim": 800,
        "export_deepflash": False
    },
    # with rois
    {
        "images": True,
        "masks": True,
        "rois": True,
        "rescaled": True,
        "z_projection": False,  # Should be performed automatically
        "masks_binary": False,  # Should be performed automatically
        "masks_png": True,
        "images_single_channel": 0,
        "x_dim": 800,  # not used if rescaled is false
        "y_dim": 800,
        "export_deepflash": False
    },
    # deepflash
    {
        "images": True,
        "masks": True,
        "rois": True,
        "rescaled": False,
        "z_projection": False,  # Should be performed automatically
        "masks_binary": False,  # Should be performed automatically
        "masks_png": True,
        "images_single_channel": 0,
        "x_dim": 0,  # not used if rescaled is false
        "y_dim": None,
        "export_deepflash": True
    }
]

# def get_test_poly(int_image):
#     _shape = int_image.data.shape
#     assert len(_shape) == 4
#     _mask_shape = (_shape[0], _shape[2], _shape[3])
#     circle_coords = skimage.draw.circle_perimeter(25,50, 10)
#     circle_coords_2 = skimage.draw.circle_perimeter(25,25, 10)
#     for z in range(len(_shape[0])):

#     assert

def get_test_label_array(int_image):
    _shape = int_image.data.shape
    assert len(_shape) == 4
    test_layer = np.zeros((_shape[0], _shape[2], _shape[3]), dtype=int)
    _ = True
    for i in range(_shape[0]):
        if _:
            test_layer[i, :10, :10] = 1
            test_layer[i, 20:30, 20:30] = 3
            _ = False
        else:
            _ = True
    return test_layer


# Frequently used Requests
def fetch_all_images(test_app_simple):
    return test_app_simple.get(
        "/api/images/fetch_all")
def read_image_from_path(test_app_simple, path):
    return test_app_simple.post(
            "/api/images/read_from_path", headers={"Content-Type": "application/json"},
            json={
                "path": path.as_posix()
            })

def make_result_layer(int_image, label_array):
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
    return int_image, int_result_layer

def delete_image_by_uid(test_app_simple, image_id):
    return test_app_simple.post(
            "/api/images/delete_by_id", headers={"Content-Type": "application/json"},
            json={
                "id": image_id
            })

def delete_all_images(test_app_simple):
    list_image_dicts = fetch_all_images(test_app_simple).json()
    ids = [img_dict["uid"] for img_dict in list_image_dicts]
    for id in ids:
        delete_image_by_uid(test_app_simple, id)