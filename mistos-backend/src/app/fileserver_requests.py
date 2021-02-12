import pickle
import os
import shutil
import json
import zarr
import pathlib
import pandas as pd

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
    return pd.read_excel(path)

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