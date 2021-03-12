# pylint:disable=no-name-in-module, import-error, no-member
import zarr
import javabridge
import bioformats
import numpy as np
import json
import xml
from app.api import utils_transformations
import app.api.classes as classes
import skimage
from skimage import exposure
import os
import pickle
from pathlib import Path
import warnings
from skimage.io import imread
import roifile
from skimage.draw import polygon2mask

# Colormaps
color_multipliers = {
    "red": [1, 0, 0],
    "green": [0, 1, 0],
    "blue": [0, 0, 1],
    "teal": [0, 1, 1],
    "yellow": [1, 1, 0]
}
cmaps = ["blue", "green", "red", "yellow", "teal"]

javabridge.start_vm(class_path=bioformats.JARS)


def start_jvm():
    javabridge.start_vm(class_path=bioformats.JARS)


def kill_jvm():
    javabridge.kill_jvm()


def read_mask(path: Path):
    # experimental feature!
    warnings.warn("Experimental Feature!")
    try:
        mask = imread(path)
    except:
        warnings.warn("Could not load image!")

    _shape = mask.shape
    print(f"shape: {_shape}")
    if len(_shape) == 6:
        mask = mask[0, :, 0, :, :, 0]
        return mask
    elif len(_shape) == 2:
        mask = mask[np.newaxis, ...]
        mask = utils_transformations.binary_mask_to_multilabel(mask)[0]
        return mask
    else:
        return None


def read_roi(path: Path, image_shape):
    rois = roifile.ImagejRoi.fromfile(path)
    if path.suffix == ".roi":
        rois = [rois]
    polys = [_.coordinates() for _ in rois]
    mask_shape_2d = (image_shape[-2], image_shape[-1])
    mask = np.zeros(mask_shape_2d)
    for i, polygon in enumerate(polys):
        polygon_mask = polygon2mask(mask_shape_2d, np.flip(polygon, axis=1))
        mask[polygon_mask] = i+1
    mask = mask[np.newaxis, ...]
    return mask


def load_metadata_only(filepath_metadata):
    '''
    loads just an images metadata
    '''
    with open(filepath_metadata, "r") as file:
        metadata_dict = json.load(file)

    return metadata_dict


def acquire_image_metadata_dict(metadata_OMEXML, filename):
    n_series = get_number_of_series(metadata_OMEXML)

    my_features = {
        "n_series": n_series,
        "original_filename": filename,
        "images": {i: {} for i in range(n_series)}
    }

    for i in range(n_series):
        my_features["images"][i]["image_name"] = metadata_OMEXML.image(i).Name
        my_features["images"][i]["image_ID"] = metadata_OMEXML.image(
            i).ID.replace(":", "_")
        my_features["images"][i]["image_acquisition_date"] = metadata_OMEXML.image(
            i).AcquisitionDate

        my_features["images"][i]["pixel_dimensions"] = metadata_OMEXML.image(
            i).Pixels.DimensionOrder
        my_features["images"][i]["pixel_type"] = metadata_OMEXML.image(
            i).Pixels.PixelType
        my_features["images"][i]["pixel_size_x"] = metadata_OMEXML.image(
            i).Pixels.SizeX
        my_features["images"][i]["pixel_size_y"] = metadata_OMEXML.image(
            i).Pixels.SizeY
        my_features["images"][i]["pixel_size_z"] = metadata_OMEXML.image(
            i).Pixels.SizeZ
        my_features["images"][i]["pixel_size_slices"] = metadata_OMEXML.image(
            i).Pixels.SizeC
        my_features["images"][i]["pixel_size_physical_x"] = metadata_OMEXML.image(
            i).Pixels.PhysicalSizeX
        my_features["images"][i]["pixel_size_physical_y"] = metadata_OMEXML.image(
            i).Pixels.PhysicalSizeY
        my_features["images"][i]["pixel_size_physical_z"] = metadata_OMEXML.image(
            i).Pixels.PhysicalSizeZ
        my_features["images"][i]["pixel_size_physical_unit_x"] = metadata_OMEXML.image(
            i).Pixels.PhysicalSizeXUnit
        my_features["images"][i]["pixel_size_physical_unit_y"] = metadata_OMEXML.image(
            i).Pixels.PhysicalSizeYUnit
        my_features["images"][i]["pixel_size_physical_unit_z"] = metadata_OMEXML.image(
            i).Pixels.PhysicalSizeZUnit

        my_features["images"][i]["n_channels"] = metadata_OMEXML.image(
            i).Pixels.channel_count  # Returns Number of Channels
        my_features["images"][i]["channel_names"] = [metadata_OMEXML.image(i).Pixels.Channel(
            n_channel).Name for n_channel in range(my_features["images"][i]["n_channels"])]

        my_features["images"][i]["custom_channel_names"] = my_features["images"][i]["channel_names"]

    return my_features


def get_number_of_series(metadata_OMEXML):
    '''
    Iterates over images in metadata_omexml. Returns number of images in series.
    '''
    for i in range(9999):
        try:
            metadata_OMEXML.image(i)
        except:
            # print(f"The imported file has {i} image series")
            break
    return i


def read_image_of_series(path, metadata_dict, n_series=0):
    '''
    Reads image number n of series from path. 
    Intensity values are rescaled to floats between 0 and 1.
    Returns zarr of shape (z,c,y,x) and metadata_dict.
    '''
    #  Start Javabridge for bioformats_importer

    tmp_reader_key = "_"

    z_dim = metadata_dict["images"][n_series]["pixel_size_z"]
    x_dim = metadata_dict["images"][n_series]["pixel_size_x"]
    y_dim = metadata_dict["images"][n_series]["pixel_size_y"]
    c_dim = metadata_dict["images"][n_series]["n_channels"]
    pixel_size_channels = metadata_dict["images"][n_series]["pixel_size_slices"]

    # Set dimensions of z stack
    z_stack = np.zeros((
        z_dim,
        c_dim,
        y_dim,
        x_dim
    ), dtype=float
    )

    for z in range(metadata_dict["images"][n_series]["pixel_size_z"]):
        with bioformats.get_image_reader(tmp_reader_key, path) as reader:

            image = reader.read(series=n_series, z=z, rescale=True)
            dim_order = reader.rdr.getDimensionOrder()
            bioformats.release_image_reader(tmp_reader_key)

        # Special Case: Greyscale Image is read as rgb
        # We transform the "rgb" image to a greyscale image
        if c_dim == 1 and pixel_size_channels == 3:
            image = skimage.color.rgb2gray(image)

        # Special Case: greyscale image
        # Greyscale images will not have a c dimension, we add it
        if c_dim == 1:
            image = image[:, :, np.newaxis]  # Has shape (x,y,c)

        # Rearrange to fit our dimension convention (c,y,x)
        image = np.moveaxis(image, -1, 0)

        z_stack[z] = image

    return (z_stack, n_series)


def read_image_file(path, n_series=-1, big_file=False):
    '''
    Function expects a filepath to a compatible image file (may be series or single image). Returns list of tuples (zarr, metadata_dict,  original_metadata)
    '''
    # First we read the metadata of our image to see what exactly we are expecting
    # Exit the function if metadata can not be read
    try:
        metadata_string = bioformats.get_omexml_metadata(path)
        metadata_OMEXML = bioformats.OMEXML(metadata_string)
    except:
        print(f"Could not read image file at {path}")
        print("Make sure it is a compatible file format!")
        return

    filename = path.split("/")[-1]
    # Check file size
    file_size = os.path.getsize(path)/10e5
    if file_size > 1000:
        big_file = True
        if n_series == -1:
            print(
                f"warning, big file with size {os.path.getsize(path)/10e5} mb detected!\nIf you import an image series consider importing only single images to prevent crashes.")

    # Create metadata dictionary
    metadata_dict = acquire_image_metadata_dict(metadata_OMEXML, filename)
    _n_series = metadata_dict["n_series"]

    # Fix metadata dict if information is missing
    for key, value in metadata_dict["images"].items():
        metadata_dict["images"][key] = fix_image_metadata(value)

    image_list = []
    if n_series == -1:
        for i in range(_n_series):
            image = read_image_of_series(path, metadata_dict, n_series=i)
            image_list.append(image)

    else:
        image = read_image_of_series(path, metadata_dict, n_series=n_series)
        image_list.append(image)

    return image_list, metadata_dict, metadata_OMEXML


def fix_image_metadata(metadata_dict):
    if not metadata_dict["pixel_size_physical_x"]:
        metadata_dict["pixel_size_physical_x"] = 1
        metadata_dict["pixel_size_physical_unit_x"] = "px"
    if not metadata_dict["pixel_size_physical_y"]:
        metadata_dict["pixel_size_physical_y"] = 1
        metadata_dict["pixel_size_physical_unit_y"] = "px"
    # dont change z
    if not len(metadata_dict["channel_names"]) == metadata_dict["n_channels"] or None in metadata_dict["channel_names"]:
        print("Channel names do not match channels!")
        metadata_dict["channel_names"] = [
            f"not_named {i}" for i in range(metadata_dict["n_channels"])]
        metadata_dict["custom_channel_names"] = [
            f"not_named {i}" for i in range(metadata_dict["n_channels"])]

    return metadata_dict


def generate_thumbnail(img, cmap_list=cmaps):
    '''
    Function expects an object of shape (z,c,y,x). To generate a thumbnail, the image is c-projected and standard color maps are applied.
    Only a maximum of 5 channels are included in the thumbnail.

    keyword arguments:
    img -- numpy array of shape (z,c,y,x)
    cmap_list -- (optional) list of colormaps to apply like:  ["blue", "green", "red", "yellow", "teal"]. By changing the order, diffrent channels will get diffrent colormaps.
    '''
    img = np.array(img).max(axis=0)

    new_shape = (img.shape[1], img.shape[2], 3)
    color_image = np.zeros(new_shape)
    n_channel = img.shape[0]

    for channel in range(n_channel):
        if channel == 5:
            break
        img_channel = img[channel]
        cmap = color_multipliers[cmaps[channel]]
        img_channel_colored = skimage.color.gray2rgb(img_channel) * cmap
        color_image += img_channel_colored

    for _color in range(color_image.shape[2]):
        _color_image = color_image[..., _color]
        _max = _color_image.max()
        _min = _color_image.min()
        if _max > 0:
            _color_image = (_color_image - _min)/_max
            color_image[..., _color] = _color_image

    # enhance contrast
    try:
        color_image = exposure.equalize_adapthist(img, clip_limit=0.1)
    except:
        color_image = (color_image + 0.01)/1.01

    color_image = (color_image*255).astype(np.uint8)
    return color_image


def import_mistos_image(input, for_experiment=False):
    '''
    Expects a path pointing to a valid exported image object file (.pkl) if for_experiment is false.
    Otherwise, expects int_image_object
    The image object holds all data to reimport a valid image into the system:
        - Image data
        - c_int_metadata json
        - Image Metadata (xml and json)
    '''
    if for_experiment == False:
        path = input
        with open(path, "rb") as file:
            int_image = pickle.load(file)
    else:
        int_image = input

    layers = int_image.image_result_layers
    measurements = int_image.result_measurements

    # Creating Layers dict: key = old_id, value = new_id
    old_image_id = int_image.uid
    id_dict = {
        "image": {old_image_id: None},
        "layers": {}
    }

    int_image.uid = -2
    int_image.image_result_layers = []
    int_image.result_measurements = []

    int_image.on_init()
    id_dict["image"][old_image_id] = int_image.uid

    for layer in layers:
        old_layer_id = layer.uid
        id_dict["layers"][old_layer_id] = None
        layer.uid = -1
        layer.image_id = int_image.uid
        layer.on_init()
        print("layer_id")
        print(layer.uid)
        id_dict["layers"][old_layer_id] = layer.uid
    print(id_dict)
    for measurement in measurements:
        print("measurement")
        print(measurement)
        measurement.uid = -1
        measurement.image_id = int_image.uid
        measurement.result_layer_id = id_dict["layers"][measurement.result_layer_id]
        measurement.on_init()

    return int_image, id_dict


def import_mistos_experiment(path):
    '''
    Expects filepath, reads archived experiment file.
    - Creates experiment without groups.
    - Iterates over experiment groups: 
    -- Imports all images
    -- Creates empty experiment group and adds these images
    -- iterates over result_layer list and adds them 
    '''
    with open(path, "rb") as file:
        int_experiment = pickle.load(file)

    new_experiment = classes.IntExperiment(
        uid=-1,
        name=int_experiment.name,
        hint=int_experiment.hint,
        description=int_experiment.description,
        tags=int_experiment.tags
    )

    new_experiment.on_init()

    for experiment_group in int_experiment.experiment_groups:
        group_image_ids = []
        group_layer_ids = []
        imported_image_ids = []
        for image in experiment_group.images:
            # id dicts are defined in import_mistos_image
            imported_image_ids.append(image.uid)
            image, id_dict = import_mistos_image(image, for_experiment=True)
            group_image_ids.append(image.uid)
            for layer_id in experiment_group.result_layer_ids:
                if layer_id in id_dict["layers"]:
                    group_layer_ids.append(id_dict["layers"][layer_id])

        new_group = classes.IntExperimentGroup(
            uid=-1,
            experiment_id=new_experiment.uid,
            name=experiment_group.name,
            hint=experiment_group.hint,
            description=experiment_group.description
        )
        new_group.on_init()
        for image_id in group_image_ids:
            new_group.add_image_by_uid(image_id)
        for layer_id in group_layer_ids:
            new_group.add_result_layer(layer_id)

        # try:
        #     new_group.calculate_result()
        # except:
        #     pass
