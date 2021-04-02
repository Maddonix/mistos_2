# import xtiff
# from SimpleITK import ImageFileWriter, GetImageFromArray
from tifffile import imsave
from skimage import img_as_ubyte, img_as_bool, img_as_uint, img_as_float32
from app import crud
import pickle
from app.api import utils_paths as utils_paths
from typing import List
from app.api.utils_transformations import rescale_image, z_project, multiclass_mask_to_binary
import numpy as np
import skimage.io
import roifile
from typing import List


def to_tiff(image_array, path, image_name, channel_names, metadata, mask=False, pixel_type=None):
    if pixel_type == "uint8":
        image_array = img_as_ubyte(image_array)
    elif pixel_type == "uint16":
        image_array = img_as_uint(image_array)
    else:
        print(
            f"Image type {pixel_type} currently not supported for export, defaulting to 32-bit float export")
        image_array = img_as_float32(image_array)
    path = path.with_name(image_name)
    path = path.with_suffix(".ome.tiff")
    imsave(
        path,
        image_array, 
        imagej=True,
        resolution = (metadata["pixel_size_physical_x"], metadata["pixel_size_physical_y"]), #x, y
        metadata={'axes': 'ZCYX', "channel_names": channel_names, "spacing": metadata["pixel_size_physical_z"], "unit":"um"}, # metadata["pixel_size_physical_unit_x"] NEED TO FIX ENCODING
    )


def to_png(array, path):
    assert array.shape[0] == 1
    assert array.shape[1] == 1
    array = array[0, 0, ...]
    # Make binary
    array = array.astype(bool)
    array = img_as_ubyte(array*255)
    skimage.io.imsave(fname=path, arr=array)


def export_mistos_image(image_uid: int):
    '''
    Expects a path and an image id. Reads c_int image from db and writes a pickle file for export.

    '''
    image = crud.read_image_by_uid(image_uid)
    path = utils_paths.make_export_mistos_object_path(image.name, "image")
    path = utils_paths.fileserver.joinpath(path)
    path = utils_paths.assert_path_not_exist(path, ".pkl")
    with open(path, "wb") as file:
        pickle.dump(image, file)
    return path


def export_mistos_experiment(experiment_uid: int):
    '''
    Experiment will be saved into a new folder with experiment group and an experiment file.

    '''
    experiment = crud.read_experiment_by_uid(experiment_uid)
    path = utils_paths.make_export_mistos_object_path(
        experiment.name, "experiment")
    path = utils_paths.fileserver.joinpath(path)
    path = utils_paths.assert_path_not_exist(path, ".pkl")

    experiment = experiment.to_int_class()
    with open(path, "wb") as file:
        pickle.dump(experiment, file)
    return path


def export_experiment_image_to_tiff(experiment, group, image, rescaled: bool, max_z: bool):
    path = utils_paths.make_export_array_name(
        image_id=image.uid,
        image_name=image.metadata["original_filename"],
        mask=False,
        group_uid=group.uid,
        group_name=group.name,
        exp_uid=experiment.uid,
        exp_name=experiment.name,
        rescaled=rescaled,
        max_z=max_z,
        png=False)
    to_tiff(
        image_array=image.data,
        path=path,
        image_name=image.metadata["original_filename"],
        channel_names=image.metadata["custom_channel_names"],
        metadata = image.metadata,
        pixel_type=image.metadata["pixel_type"]
    )


def export_experiment_images(
        experiment,
        group,
        image,
        export_rescaled: bool,
        export_single_channel: int,
        export_max_z_project: bool,
        x_dim: int = 1024,
        y_dim: int = 1024):
    '''
    '''
    image_array = image.data
    if export_single_channel > -1:
        image_array = image_array[:, export_single_channel, ...]
        image_array = image_array[:, np.newaxis, ...]
        image.metadata["custom_channel_names"] = [
            image.metadata["custom_channel_names"][export_single_channel]]
    if export_max_z_project:
        image_array = z_project(image_array)
    if export_rescaled:
        image.data = image_array
        export_experiment_image_to_tiff(
            experiment, group, image, rescaled=False, max_z=export_max_z_project)
        image_array = rescale_image(image_array, x_dim, y_dim)
    image.data = image_array
    export_experiment_image_to_tiff(
        experiment, group, image, rescaled=export_rescaled, max_z=export_max_z_project)


def export_experiment_mask(experiment, group, mask, image, channel_names, rescaled: bool, max_z: bool, png: bool):
    path = utils_paths.make_export_array_name(
        image_id=image.uid,
        image_name=image.metadata["original_filename"],
        mask=True,
        group_uid=group.uid,
        group_name=group.name,
        exp_uid=experiment.uid,
        exp_name=experiment.name,
        rescaled=rescaled,
        max_z=max_z,
        png=png)
    if png:
        to_png(mask, path)
    else:
        to_tiff(image_array=mask,
                path=path,
                image_name=image.metadata["original_filename"],
                channel_names=channel_names, metadata = image.metadata, mask=True)


def export_experiment_roi(experiment, group, rois: List[roifile.ImagejRoi], int_image):
    path = utils_paths.make_export_roi_folder_name(
        image_id=int_image.uid,
        image_name=int_image.metadata["original_filename"],
        group_uid=group.uid,
        group_name=group.name,
        exp_uid=experiment.uid,
        exp_name=experiment.name)
    for i, roi in enumerate(rois):
        roi.tofile(path.joinpath(f"{i}").with_suffix(".roi").as_posix())


def export_experiment_masks(
        experiment,
        group,
        result_layer_id,
        export_binary,
        export_png,
        export_rescaled: bool,
        export_max_z_project: bool,
        export_rois: bool,
        x_dim: int = 1024,
        y_dim: int = 1024):
    '''

    '''
    result_layer = crud.read_result_layer_by_uid(
        result_layer_id).to_int_class()
    int_image = crud.read_db_image_by_uid(
        result_layer.image_id).to_int_class()
    mask_array = result_layer.data
    mask_array = mask_array[:, np.newaxis, ...]
    # Mask has only one channel, which is named after the layer
    channel_names = [result_layer.name]
    if export_rois:  # only 2d!
        roi_array = z_project(mask_array)[0, 0, ...]
        contours = [label.astype(
            int)+1 for label in skimage.measure.find_contours(roi_array, level=0.5)]
        rois = [roifile.ImagejRoi.frompoints(
            np.flip(poly, axis=1)) for poly in contours]
        export_experiment_roi(experiment, group, rois, int_image)
    if export_binary or export_png:
        mask_array, label_list = multiclass_mask_to_binary(
            mask_array)
    if export_max_z_project or export_png:  # OVERLAPPING LABELS WILL TAKE VALUE OF HIGHEST LABEL
        mask_array = z_project(mask_array)
    if export_binary:
        mask_array = mask_array.astype(bool)
    if export_rescaled:
        export_experiment_mask(experiment, group, mask_array, int_image,
                               channel_names, False, export_max_z_project, export_png)
        mask_array = rescale_image(mask_array, x_dim, y_dim)
    export_experiment_mask(experiment, group, mask_array, int_image,
                           channel_names, export_rescaled, export_max_z_project, export_png)
