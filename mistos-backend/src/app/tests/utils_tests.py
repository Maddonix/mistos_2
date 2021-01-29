import pathlib
import app.api.utils_import as utils_import
import zarr
from app.api import classes_internal as c_int

testcase_path = pathlib.Path("F:/Data_Storage/AG_Rittner/Microscope Framework/data/raw/tests")
test_paths = [
    '0_test_czi.czi',
    '0_test_oib.oib',
    '0_test_tif.tif',
    # '1_test_lif.lif',
    '1_test_tif.tif',
    '2_test_tif.tif'
    ]

_test_paths = [testcase_path.joinpath(_).as_posix() for _ in test_paths]

def import_test_images():
    for test_case in _test_paths:
        print("________________________")
        print(test_case)
        if test_case == 'F:/Data_Storage/AG_Rittner/Microscope Framework/data/raw/tests/1_test_lif.lif':
            print("single_import")
            image_list, metadata_dict, metadata_OMEXML = utils_import.read_image_file(test_case, n_series = 0)
        else:
            image_list, metadata_dict, metadata_OMEXML = utils_import.read_image_file(test_case)
        for image, i in image_list:
            img_zarr = zarr.creation.array(image)
            
            int_image = c_int.IntImage(
                uid = -1,
                series_index = i,
                name = metadata_dict["original_filename"],
                metadata = metadata_dict, # This is not the finished metadata!
                data = img_zarr,
                metadata_omexml = metadata_OMEXML
                )
            int_image.on_init()


