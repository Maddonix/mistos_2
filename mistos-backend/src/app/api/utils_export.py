import xtiff
from app import crud
import pickle
from app.api import classes_internal as c_int
from app.api import utils_paths as utils_paths

def to_tiff(image_array, path, image_name, channel_names, mask=False):
    if mask == True:
        image_array = image_array.astype(int)
    else: 
        image_array = image_array.astype(int)
    xtiff.to_tiff(
        img = image_array,
        file = path,
        image_name = image_name, 
        channel_names = channel_names
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
