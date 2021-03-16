import pickle
import os
import shutil
import json
import zarr
import pathlib
import pandas as pd
import imageio
from shutil import copyfile
from typing import List
import xml


def create_folder(path: pathlib.Path):
    os.mkdir(path)


def delete_file(path: pathlib.Path):
    os.remove(path)


def delete_folder(path: pathlib.Path):
    shutil.rmtree(path)


def save_deepflash_model(model_input_paths: List[pathlib.Path], path: pathlib.Path):
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


def load_deepflash_model(path: pathlib.Path):
    with open(path, "rb") as _file:
        model = pickle.load(_file)
    return model


def save_zarr(array, path: pathlib.Path):
    path = path.as_posix()
    zarr.save_array(path, array)


def load_zarr(path: pathlib.Path):
    path = path.as_posix()
    return zarr.convenience.load(path)


def save_json(dictionary: dict, path: pathlib.Path):
    with open(path, "w") as file:
        json.dump(dictionary, file, indent=3)


def load_json(path):
    with open(path, "r") as file:
        dictionary = json.load(file)
    return dictionary


def save_thumbnail(image, path: pathlib.Path):
    '''
    image format?
    '''
    imageio.imwrite(path, image)


def save_measurement(measurement:dict, path: pathlib.Path):
    '''
    dictionary
    '''
    with open(path, "wb") as _file:
        pickle.dump(measurement, _file)


def load_measurement(path: pathlib.Path):
    with open(path, "rb") as _file:
        measurement = pickle.load(_file)
    return measurement


def save_measurement_summary(measurement_summary: dict, path: pathlib.Path):
    with open(path, "w") as _file:
        json.dump(measurement_summary, _file)


def load_measurement_summary(path: pathlib.Path):
    with open(path, "r") as _file:
        measurement_summary = json.load(_file)
    return measurement_summary


def save_result_df(result_df, path: pathlib.Path):
    result_df.to_excel(path)


def load_result_df(path: pathlib.Path):
    return pd.read_excel(path, index_col=0)


def save_metadata(metadata, path: pathlib.Path):
    with open(path, "w") as _file:
        json.dump(metadata, _file)


def save_metadata_xml(metadata: str, path: pathlib.Path):
    with open(path, "w", encoding="utf-8") as file:
        file.write(metadata)


def load_metadata_xml(path: pathlib.Path):
    path = path.as_posix()
    return xml.dom.minidom.parse(path)


def save_classifier(clf, path: pathlib.Path):
    with open(path, "wb") as _file:
        pickle.dump(clf, _file)


def load_classifier(path: pathlib.Path):
    with open(path, "rb") as _file:
        clf = pickle.load(_file)
    return clf


def save_classifier_test_train(test_train, path: pathlib.Path):
    with open(path, "wb") as _file:
        pickle.dump(test_train, _file)


def load_classifier_test_train(path: pathlib.Path):
    with open(path, "rb") as _file:
        test_train = pickle.load(_file)
    return test_train
