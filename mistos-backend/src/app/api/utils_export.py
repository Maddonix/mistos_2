import xtiff
from tifffile import imwrite
from skimage import img_as_ubyte, img_as_bool, img_as_uint, img_as_float32
from app import crud
import pickle
from app.api import classes_internal as c_int
from app.api import utils_paths as utils_paths

def to_tiff(image_array, path, image_name, channel_names, mask=False, pixel_type = None):
    if mask == True:
        image_array = img_as_bool(image_array)
    else: 
        if pixel_type == "uint8":
            image_array = img_as_ubyte(image_array)
        elif pixel_type == "uint16":
            image_array = img_as_uint(image_array)
        else:
            print(f"Image type {pixel_type} currently not supported for export, defaulting to 32-bit float export")
            image_array = img_as_float32(image_array)
    xtiff.to_tiff(
        img = image_array,
        file = path,
        image_name = image_name, 
        channel_names = channel_names,
        profile = 3
    )

def export_mistos_image(image_uid:int):
    '''
    Expects a path and an image id. Reads c_int image from db and writes a pickle file for export.
    
    '''
    image = crud.read_image_by_uid(image_uid)
    path = utils_paths.make_export_mistos_object_path(image.name, "image")
    path = utils_paths.fileserver.joinpath(path)
    path = utils_paths.assert_path_not_exist(path, ".pkl")
    with open(path, "wb") as file:
        pickle.dump(image, file)

def export_mistos_experiment(experiment_uid:int):
    '''
    Experiment will be saved into a new folder with experiment group and an experiment file.
    
    '''
    experiment = crud.read_experiment_by_uid(experiment_uid)
    path = utils_paths.make_export_mistos_object_path(experiment.name, "experiment")
    path = utils_paths.fileserver.joinpath(path)
    path = utils_paths.assert_path_not_exist(path, ".pkl")
     
    experiment = experiment.to_int_class()
    with open(path, "wb") as file:
        pickle.dump(experiment, file)
