import json
import os
import pathlib
from app.api import utils_paths
from app import fileserver_requests

# Garbage is not located on fileserver. Should be a local instance.
garbage_json = pathlib.Path("garbage.json")
filepath_garbage_json = garbage_json.as_posix()

def create_garbage_json(filepath_garbage_json = filepath_garbage_json):
    '''
    Expects Path to garbage json file
    '''
    empty = {
                "filelist": [],
                "folderlist": []
            
            }
    with open(filepath_garbage_json, "w") as _file:
        json.dump(empty, _file)

def add_file_to_garbage(filepath_item, filepath_garbage_json = filepath_garbage_json):
    '''
    Expects filepath to single file
    '''
    with open(filepath_garbage_json, "r") as _file:
        garbage = json_load(_file)

    garbage["filelist"].append(filepath_item)

    with open(filepath_garbage_json, "w") as _file:
        json.dump(garbage, _file)

def add_folder_to_garbage(filepath_folder, filepath_garbage_json = filepath_garbage_json):
    '''
    Expects filepath to folder
    '''
    with open(filepath_garbage_json, "r") as _file:
        garbage = json_load(_file)

    garbage["folderlist"].append(filepath_item)

    with open(filepath_garbage_json, "w") as _file:
        json.dump(garbage, _file)


def delete_garbage(filepath_garbage_json = filepath_garbage_json):
    '''
    reads garbage json and deletes all files and folders
    '''
    with open(filepath_garbage_json, "r") as _file:
        garbage = json_load(_file)

    for filepath in garbage["filelist"]:
        fileserver_requests.delete_file(filepath)

    for filepath in garbage["folderlist"]:
        fileserver_requests.delete_folder(filepath)

    delete_garbage_file()
    create_garbage_json()

def delete_garbage_file(filepath_garbage_json = filepath_garbage_json):
    
    os.remove(filepath_garbage_json)


