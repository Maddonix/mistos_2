import pathlib
import os
from datetime import datetime as dt

########## MAKE SURE ALL FOLDERS EXIST ON STARTUP, ELSE CREATE ###############
fileserver = pathlib.Path("F:\\Data_Storage\\AG_Rittner\\Microscope Framework\\data\\fileserver_folder")
export_folder = pathlib.Path("F:\\Data_Storage\\AG_Rittner\\Microscope Framework\\data\\fileserver_folder\\export")

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

for path in check_paths_list:
    if not path.exists():
        os.mkdir(path)
        
def make_image_path(uid):
    path = image_folder.joinpath(f"{uid}.zarr").as_posix()
    return path

def make_metadata_path(uid):
    path = metadata_folder.joinpath(f"{uid}.json").as_posix()
    return path

def make_result_layer_path(uid):
    path = result_layers_folder.joinpath(f"{uid}.zarr").as_posix()
    return path

def make_result_path(uid):
    path = result_folder.joinpath(f"{uid}.xlsx").as_posix()
    return path

def make_measurement_path(uid):
    path = measurement_folder.joinpath(f"{uid}.zarr").as_posix()
    return path

def make_measurement_summary_path(uid):
    path = measurement_folder.joinpath(f"{uid}.pkl").as_posix()
    return path

def make_clf_path(uid):
    path = clf_folder.joinpath(f"clf_{uid}.pkl").as_posix()
    return path

def make_clf_test_train_path(uid):
    path = clf_folder.joinpath(f"data_{uid}.pkl").as_posix()
    return path

def make_tmp_file_path(filename):
    filelist = [_ for _ in tmp_folder.glob("*")]
    path = tmp_folder.joinpath(f"{len(filelist)}_{filename}").as_posix()
    return path

####### EXPORT PATHS
def make_experiment_export_folder_path(uid, experiment_name):
    '''
    Expects Experiment ID and name, doesnt return string, but path object
    '''
    path = export_folder.joinpath(f"{uid}_{experiment_name}") #_{dt.now().strftime('%Y.%m.%d %Hh %Mmin %Ss')}

    return path

def create_experiment_export_folder(uid, experiment_name):
    path = make_experiment_export_folder_path(uid, experiment_name)
    if not path.exists():
        os.mkdir(path.as_posix())

def make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name):
    print(f"make_experiment_group_export_folder_path:")
    experiment_path = make_experiment_export_folder_path(exp_uid, exp_name)
    experiment_group_path = experiment_path.joinpath(f"{group_uid}_{group_name}")
    print(experiment_group_path)
    return experiment_group_path

def create_experiment_group_export_folder(group_uid, group_name, exp_uid, exp_name):
    path = make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name)
    if not path.exists():
        os.mkdir(path.as_posix())

def make_images_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled = False):
    if rescaled:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("images_rescaled")
    else:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("images")

def create_images_export_folder(group_uid, group_name, exp_uid, exp_name, rescaled = False):
    path = make_images_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled)
    if not path.exists():
        os.mkdir(path.as_posix())

def make_masks_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled = False):
    if rescaled:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("masks_rescaled")
    else:
        return make_experiment_group_export_folder_path(group_uid, group_name, exp_uid, exp_name).joinpath("masks")

def create_masks_export_folder(group_uid, group_name, exp_uid, exp_name, rescaled = False):
    path = make_masks_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled)
    if not path.exists():
        os.mkdir(path.as_posix())

def make_experiment_export_df_name(uid, experiment_name):
    experiment_export_folder = make_experiment_export_folder_path(uid, experiment_name)
    export_name = experiment_export_folder.joinpath("measurement_summary.xlsx").as_posix()
    return export_name

def make_export_array_name(image_id, image_name, mask, group_uid, group_name, exp_uid, exp_name, rescaled):
    if mask == False:
        path = make_images_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled)
    else:
        path = make_masks_export_folder_path(group_uid, group_name, exp_uid, exp_name, rescaled)

    export_name = path.joinpath(f"{image_id}_{image_name}.tiff").as_posix()
    return export_name

############ Names
def make_measurement_name(image_name, label_layer_name):
    return f"measurement_{label_layer_name}_in_{image_name}"

######################## Testing
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
    testcase_path = testcase_path.joinpath("processed", f"{filename}_{index}.json")
    return testcase_path