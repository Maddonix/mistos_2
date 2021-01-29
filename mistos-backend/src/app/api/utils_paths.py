import pathlib

########## MAKE SURE ALL FOLDERS EXIST ON STARTUP, ELSE CREATE ###############
fileserver = pathlib.Path("F:\\Data_Storage\\AG_Rittner\\Microscope Framework\\data\\fileserver_folder")

image_folder = pathlib.Path("images")
metadata_folder = pathlib.Path("metadata")
result_layers_folder = pathlib.Path("result_layers")
result_folder = pathlib.Path("results")
measurement_folder = pathlib.Path("measurements")
clf_folder = pathlib.Path("classifiers")

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
    path = result_folder.joinpath(f"{uid}.zarr").as_posix()
    return path

def make_measurement_path(uid):
    path = measurement_folder.joinpath(f"{uid}.pkl").as_posix()
    return path

def make_clf_path(uid):
    path = clf_folder.joinpath(f"clf_{uid}.pkl").as_posix()
    return path

def make_clf_test_train_path(uid):
    path = clf_folder.joinpath(f"data_{uid}.pkl").as_posix()
    return path

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