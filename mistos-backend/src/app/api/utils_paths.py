import pathlib
import os
from datetime import datetime as dt
import cfg

# Default dirs
default_mistos_dir = pathlib.Path.home()
default_export_dir = default_mistos_dir.joinpath("export")
default_fileserver_dir = default_mistos_dir.joinpath("working_directory")
using_default = False

# Check if custom paths were supplied
custom_paths = cfg.settings

# Ceck for custom export_folder path
export_folder = pathlib.Path(custom_paths["EXPORT_DIRECTORY"])
if export_folder.as_posix() == ".":
    using_default = True
    export_folder = default_export_dir
    print(f"Export Directory is: {default_export_dir}")
elif not export_folder.exists():
    using_default = True
    print("WARNING: export path was set to:")
    print(export_folder)
    print("Path doesn't exist, using default export directory")
    print(default_export_dir)
    using_default = True
    export_folder = default_export_dir
else:
    print("Custom Export Directory:")
    print(export_folder)

# Check for custom fileserver_path
fileserver = pathlib.Path(custom_paths["WORKING_DIRECTORY"])
if fileserver.as_posix() == ".":
    using_default = True
    fileserver = default_fileserver_dir
    print(f"Export Directory is: {default_fileserver_dir}")
elif not fileserver.exists():
    using_default = True
    print("WARNING: export path was set to:")
    print(fileserver)
    print("Path doesn't exist, using default export directory")
    print(default_fileserver_dir)
    using_default = True
    fileserver = default_fileserver_dir
else:
    print("Custom Export Directory:")
    print(fileserver)

if using_default and not default_mistos_dir.exists():
    os.mkdir(default_mistos_dir)


static_fileserver = "localhost:7778/"

image_folder = pathlib.Path("images")
metadata_folder = pathlib.Path("metadata")
result_layers_folder = pathlib.Path("result_layers")
result_folder = pathlib.Path("results")
measurement_folder = pathlib.Path("measurements")
clf_folder = pathlib.Path("classifiers")
tmp_folder = pathlib.Path("_tmp")


check_paths_list = [
    "",
    image_folder,
    metadata_folder,
    result_layers_folder,
    result_folder,
    measurement_folder,
    clf_folder,
    tmp_folder
]
check_paths_list = [fileserver.joinpath(path) for path in check_paths_list]
check_paths_list.append(export_folder)

for path in check_paths_list:
    if not path.exists():
        os.mkdir(path)


def add_str_to_path(path, _str):
    _ = path.as_posix()
    _ = _+_str
    return pathlib.Path(_)


def assert_path_not_exist(_path, suffix):
    '''
    Expects a pathlib Path. Checks if path exists and appends [{i}]{suffix} until it doesnt.
    '''
    i = 0
    if add_str_to_path(_path, suffix).exists():
        path = add_str_to_path(_path, f" [{i}]{suffix}")
        while path.exists():
            i += 1
            path = add_str_to_path(_path, f" [{i}]{suffix}")
    else:
        path = add_str_to_path(_path, suffix)
    return path


def make_image_path(uid):
    path = image_folder.joinpath(f"{uid}.zarr")
    return path


def make_thumbnail_path(uid):
    path = image_folder.joinpath(f"{uid}.png")
    return path


def make_metadata_path(uid: int):
    path = metadata_folder.joinpath(f"{uid}.json")
    return path


def make_metadata_xml_path_from_json_path(path: pathlib.Path):
    ''' Function expects a pathlib.Path and changes extension to ".xml"'''
    return path.with_suffix(".xml")


def make_result_layer_path(uid):
    path = result_layers_folder.joinpath(f"{uid}.zarr")
    return path


def make_result_path(uid):
    path = result_folder.joinpath(f"{uid}.xlsx")
    return path


def make_measurement_path(uid):
    path = measurement_folder.joinpath(f"{uid}.pkl")
    return path


def make_measurement_summary_path(uid):
    path = measurement_folder.joinpath(f"{uid}_summary.json")
    return path


def make_clf_path(uid):
    path = clf_folder.joinpath(f"clf_{uid}.pkl")
    return path


def make_clf_test_train_path(uid: int):
    path = clf_folder.joinpath(f"data_{uid}.pkl")
    return path


def make_tmp_file_path(filename: str) -> pathlib.Path:
    '''
    Exoects filename, returns enumerated filename in tmp_folder
    '''
    filelist = [_ for _ in tmp_folder.glob("*")]
    path = tmp_folder.joinpath(f"{len(filelist)}_{filename}")
    return path


def make_deepflash_model_path(uid):
    path = clf_folder.joinpath(f"deepflash_model_{uid}")
    return path


def make_export_mistos_object_path(name: str, type: str):
    path = export_folder.joinpath(f"mistos_{type}_{name}")
    return path


# EXPORT PATHS
def make_experiment_export_folder_path(uid, experiment_name):
    '''
    Expects Experiment ID and name, doesnt return string, but path object
    '''
    path = export_folder.joinpath(
        f"{uid}_{experiment_name}")  # _{dt.now().strftime('%Y.%m.%d %Hh %Mmin %Ss')}

    return path


def create_experiment_export_folder(uid, experiment_name):
    path = make_experiment_export_folder_path(uid, experiment_name)
    if not path.exists():
        os.mkdir(path)


def make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name):
    print(f"make_experiment_group_export_folder_path:")
    experiment_path = make_experiment_export_folder_path(exp_uid, exp_name)
    experiment_group_path = experiment_path.joinpath(
        f"{group_uid}_{group_name}")
    print(experiment_group_path)
    return experiment_group_path


def create_experiment_group_export_folder(group_uid, group_name, exp_uid, exp_name):
    path = make_experiment_group_export_folder_path(
        group_uid, group_name, exp_uid, exp_name)
    if not path.exists():
        os.mkdir(path)


def make_images_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled=False):
    if rescaled:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("images_rescaled")
    else:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("images")


def create_images_export_folder(group_uid, group_name, exp_uid, exp_name, rescaled=False):
    path = make_images_export_folder_path(
        group_uid, group_name, exp_uid, exp_name, rescaled)
    if not path.exists():
        os.mkdir(path)


def make_rois_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled=False):
    if rescaled:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("rois_rescaled")
    else:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("rois")


def create_rois_export_folder(group_uid, group_name, exp_uid, exp_name, rescaled=False):
    path = make_rois_export_folder_path(
        group_uid, group_name, exp_uid, exp_name, rescaled)
    if not path.exists():
        os.mkdir(path)


def make_masks_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled=False):
    if rescaled:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("masks_rescaled")
    else:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("masks")


def create_masks_export_folder(group_uid, group_name, exp_uid, exp_name, rescaled=False):
    path = make_masks_export_folder_path(
        group_uid, group_name, exp_uid, exp_name, rescaled)
    if not path.exists():
        os.mkdir(path)


def make_experiment_export_df_name(uid, experiment_name):
    experiment_export_folder = make_experiment_export_folder_path(
        uid, experiment_name)
    export_name = experiment_export_folder.joinpath(
        "measurement_summary.xlsx")
    return export_name


def make_export_array_name(image_id, image_name, mask, group_uid, group_name, exp_uid, exp_name, rescaled, max_z: bool, png=False):
    if mask == False:
        path = make_images_export_folder_path(
            group_uid, group_name, exp_uid, exp_name, rescaled)
    else:
        path = make_masks_export_folder_path(
            group_uid, group_name, exp_uid, exp_name, rescaled)
    image_name = pathlib.Path(image_name).with_suffix("").as_posix()
    # export_name = path.joinpath(image_name)
    if max_z:
        image_name = f"{image_name}_max_z"
    if mask:
        image_name = f"{image_name}_mask"

    
    if png:
        image_name = image_name + ".png"
    else:
        image_name = image_name + ".tiff"
    export_name = path.joinpath(image_name)
    return export_name


def make_export_roi_folder_name(
        image_id: int,
        image_name: str,
        group_uid: int,
        group_name: str,
        exp_uid: int,
        exp_name: int) -> pathlib.Path:
    path = make_rois_export_folder_path(
        group_uid, group_name, exp_uid, exp_name, False)
    image_name = pathlib.Path(image_name).with_suffix("").as_posix()
    folder_name = path.joinpath(f"{image_id}_{image_name}")
    if not folder_name.exists():
        os.mkdir(folder_name)
    return folder_name


# Names


def make_measurement_name(image_name, label_layer_name):
    return f"measurement_{label_layer_name}_in_{image_name}"

# Testing


def make_test_path_image_raw(filename):
    testcase_path = pathlib.Path("testcases")
    testcase_path = testcase_path.joinpath("raw", filename)
    return testcase_path


def make_test_path_image_processed(filename, index):
    testcase_path = pathlib.Path("testcases")
    testcase_path = testcase_path.joinpath("processed", f"{filename}_{index}")
    return testcase_path


def make_test_path_metadata(filename, index):
    testcase_path = pathlib.Path("testcases")
    testcase_path = testcase_path.joinpath(
        "processed", f"{filename}_{index}.json")
    return testcase_path
