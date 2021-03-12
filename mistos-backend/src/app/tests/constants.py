import pathlib
import numpy as np
from app.api.classes import *
from app.api.classes_com import *

test_images_folder = pathlib.Path("../../tutorial/Demo Experiment 1")
deepflash_model_folder = pathlib.Path(
    r"F:\Data_Storage\AG_Rittner\Microscope Framework\data\demo_experiment_deepflash\model")

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
    None
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
        "y_dim": 1024
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
        "y_dim": 1024
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
        "y_dim": 1024
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
        "y_dim": 1200
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
        "y_dim": 700
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
        "y_dim": 1400
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
        "y_dim": 800
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
        "y_dim": 800
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
        "y_dim": 800
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
        "y_dim": 800
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
        "y_dim": 800
    }
]


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
