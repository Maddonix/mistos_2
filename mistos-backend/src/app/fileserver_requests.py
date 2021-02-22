import pickle
import os
import shutil
import json
import zarr
import pathlib
import pandas as pd
import imageio
from app.api import utils_garbage
from shutil import copyfile


def create_folder(path):
    os.mkdir(path)

def check_path_exists(path):
    '''
    if path leads to file or folder, return true
    '''
    _path = pathlib.Path(path)
    if _path.exists():
        return True
    else:
        return False

def delete_file(path):
    try:
        os.remove(path)
    except:
        print(f"file {path} could not be deleted. Add to garbage collection")
        utils_garbage.add_folder_to_garbage(path)

def delete_folder(path):
    try:
        shutil.rmtree(path)
    except:
        print(f"folder {path} could not be deleted. Add to garbage collection")
        utils_garbage.add_folder_to_garbage(path)

def save_deepflash_model(model_input_paths, path):
    '''
    keyword arguments:
    model_input_paths -- list of pathlib.Path objects pointing to model files
    path -- pathlib.Path to create the new model folder
    '''
    print(model_input_paths)
    print(path)

    # Create new folder to save models in
    path = pathlib.Path(path)
    create_folder(path)
    for input_path in model_input_paths:
        model_path = path.joinpath(input_path.as_posix().split("/")[-1])
        copyfile(input_path, model_path)
        
def load_deepflash_model(path):
    with open(path, "rb") as _file:
        model = pickle.load(_file)
    return model

def save_zarr(array, path):
    zarr.save_array(path,array)

def save_json(dictionary, path):
    with open(path, "w") as file:
        json.dump(dictionary, file, indent = 3)

def save_thumbnail(image, path):
    imageio.imwrite(path, image)

def save_measurement(measurement, path):
    print(measurement)
    print(type(measurement))
    print(measurement.shape)
    zarr.save_array(path, measurement)
    
def load_measurement(path):
    measurement = zarr.convenience.load(path)
    return measurement

def save_measurement_summary(measurement_summary, path):
    with open(path, "w") as _file:
        json.dump(measurement_summary, _file)

def load_measurement_summary(path):
    with open(path, "r") as _file:
        measurement_summary = json.load(_file)
    return measurement_summary

def save_result_df(result_df, path):
    result_df.to_excel(path)

def load_result_df(path):
    return pd.read_excel(path, index_col = 0)

def load_metadata(path):
    with open(path, "r") as _file:
        metadata = json.load(_file)
    return metadata

def save_metadata(metadata, path): 
    with open(path, "w") as _file:
        json.dump(metadata, _file)

def save_classifier(clf, path):
    with open(path, "wb") as _file:
        pickle.dump(clf, _file)

def load_classifier(path):
    with open(path, "rb") as _file:
        clf = pickle.load(_file)
    return clf

def save_classifier_test_train(test_train, path):
    with open(path, "wb") as _file:
        pickle.dump(test_train, _file)

def load_classifier_test_train(path):
    with open(path, "rb") as _file:
        test_train = pickle.load(_file)
    return test_train