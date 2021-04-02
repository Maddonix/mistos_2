from deepflash2.learner import EnsembleLearner, get_files, Path
from app import crud
import pathlib
import numpy as np
from app.api import classes, utils_transformations
import app.fileserver_requests as fsr
from app.api import utils_paths


def predict_image_list(classifier_id, image_id_list, use_tta, channel=0, transform_to_multilabel=True, separate_z_slices=False):
    '''
    Predict a list of images. If separate_z_slices is False we make a max_z_projection of the image and it only works with greyscale images. If separate_z_slices is True we have to pass a channel which will be selected
    Furthermore, all z-slices will be temporarily exported as single images of only the selected channel.

    keyword arguments:
    image_id_list -- list of integers, integers must be valid image uids
    classifier_id -- integer, must be valid classifier uid; classifier must be of type "deepflash_model"
    use_tta -- boolean, if true tta prediction is used. Image will be predicted in multiple orientations, consensus is returned. Takes significantly longer, yiels more reliable results
    separate_z_slices -- boolean, if True each z slice of each image will be temporarily stored and passed to the prediction.
    '''
    tmp_filepaths = []
    # Read image paths
    if separate_z_slices == False:
        tmp_indexes = []
        image_list = [crud.read_image_by_uid(
            image_id) for image_id in image_id_list]
        image_path_list = [pathlib.Path(
            crud.read_db_image_by_uid(int_image.uid).path_image) for int_image in image_list]
        # Check dimensions of images
        for i, image in enumerate(image_list):
            print(image.data.shape)
            # Means this image is a z stack
            if image.data.shape[0] > 1 or image.data.shape[1] > 1:
                # image_array = image.select_channel(channel)
                image_array = utils_transformations.z_project(
                    image_array, mode="max")
                print(
                    f"shape of {image.name} was changed from {image.data.shape} to {image_array.shape}")
                tmp_filepath = utils_paths.make_tmp_file_path(
                    f"{image.uid}_0.zarr")
                fsr.save_zarr(image_array, tmp_filepath)
                tmp_filepaths.append(tmp_filepath)
                tmp_indexes.append(i)
                image_path_list[i] = tmp_filepath

    else:
        print("3D Prediction Mode")
        print("extracting z-slices to tmp folder")
        image_path_list = []
        layer_dict = {}  # {image_uid: [filepath]}
        for image_id in image_id_list:
            print(f"Splitting image {image_id}")
            image = crud.read_image_by_uid(image_id)
            layer_dict[image_id] = []
            for n_layer in range(image.data.shape[0]):
                print(f"layer: {n_layer}")
                layer = image.data[n_layer, channel, ...]
                layer = layer[np.newaxis, np.newaxis, ...]
                print(layer.shape)
                path = utils_paths.make_tmp_file_path(
                    f"{image.uid}_{n_layer}.zarr")
                tmp_filepaths.append(path)
                fsr.save_zarr(layer, path)
                image_path_list.append(path)
                layer_dict[image_id].append([])

        image_path_list = [pathlib.Path(path) for path in image_path_list]

    # Read classifier path
    classifier = crud.read_classifier_by_uid(classifier_id)
    assert classifier.clf_type == "deepflash_model"
    classifier_path = pathlib.Path(classifier.classifier)

    # Create EnsembleLearner and read model
    # , dl_kwargs={'num_workers':0}) # num_workers set to 0 due to cuda error on windows workiing with shared storage
    el = EnsembleLearner(files=image_path_list)#, dl_kwargs={'num_workers':0})
    el.get_models(classifier_path)

    # Pass image file paths to ensemble learner and predict images
    el.get_ensemble_results(image_path_list, use_tta=use_tta)
    if separate_z_slices == False:
        for i, path in enumerate(el.df_ens["res_path"]):
            path = pathlib.Path(path)
            print(path)
            if i in tmp_indexes:
                image_id, n_layer, segmentation = get_segmentation_from_tmp_path(
                    path)
            else:
                image_id, segmentation = get_segmentation_from_path(path)
            # DeepFlash provides 2d segmentation only right now, therefore we have to change the dimension
            int_image = crud.read_image_by_uid(image_id)
            if len(segmentation.shape) == 2:
                segmentation_reshaped = np.zeros(
                    (
                        int_image.data.shape[0],
                        int_image.data.shape[2],
                        int_image.data.shape[3]
                    )
                )

                for z in range(int_image.data.shape[0]):
                    segmentation_reshaped[z] = segmentation
                segmentation = segmentation_reshaped

            # Transform to multilabel
            if transform_to_multilabel:
                segmentation = utils_transformations.binary_mask_to_multilabel(segmentation)[
                    0]

            # Create new Result Layer
            result_layer = classes.IntImageResultLayer(
                uid=-1,
                name=f"df_seg_{classifier.uid}_{classifier.name}",
                hint=f"Segmentation was created using DeepFlash2 (model: {classifier.name}, [ID: {classifier.uid}]",
                image_id=image_id,
                layer_type="labels",
                data=segmentation
            )

            result_layer.on_init()

            # Measure Mask in image
            int_image.refresh_from_db()
            int_image.measure_mask_in_image(result_layer.uid)

    else:
        for path in el.df_ens["res_path"]:
            image_id, n_layer, segmentation = get_segmentation_from_tmp_path(
                path)
            layer_dict[image_id][n_layer] = segmentation

        for image_id, segmentation_list in layer_dict.items():
            print(segmentation_list[0].shape)
            y_dim = segmentation_list[0].shape[0]
            x_dim = segmentation_list[0].shape[1]
            result_layer_data = np.zeros(
                (len(segmentation_list), y_dim, x_dim), dtype=bool)
            for i, segmentation in enumerate(segmentation_list):
                result_layer_data[i] = segmentation

            if transform_to_multilabel:
                result_layer_data = utils_transformations.binary_mask_to_multilabel(
                    result_layer_data)[0]

            result_layer = classes.IntImageResultLayer(
                uid=-1,
                name=f"df_seg_{classifier.uid}_{classifier.name}",
                hint=f"Segmentation was created using DeepFlash2 (model: {classifier.name}, [ID: {classifier.uid}], channel number: {channel}, 3D Mode",
                image_id=image_id,
                layer_type="labels",
                data=result_layer_data
            )

            result_layer.on_init()
            int_image = crud.read_image_by_uid(image_id)
            int_image.measure_mask_in_image(result_layer.uid)

    # delete temp files
    el.clear_tmp()
    for path in tmp_filepaths:
        fsr.delete_folder(path)


def get_segmentation_from_path(path):
    '''
    takes path as pathlib.path and returns a tuple containing id and segmentation array with shape (z,y,x)

    returns: (uid, array) 
    '''
    print(path)
    uid = int(path.as_posix().split("/")[-1].split(".")[0])
    segmentation_array = np.load(path)["seg"]
    segmentation_array = np.where(segmentation_array > 0.5, 1, 0)
    segmentation_array.astype(np.bool)

    return(uid, segmentation_array)


def get_segmentation_from_tmp_path(path):
    '''
    takes path as pathlib.path and returns a tuple containing id, n_layer and segmentation array with shape (z,y,x)

    returns: (uid, array) 
    '''
    _name = path.as_posix().split("/")[-1].split(".")[0]
    uid = int(_name.split("_")[-2])
    n_layer = int(_name.split("_")[-1])
    segmentation_array = np.load(path)["seg"]
    segmentation_array = np.where(segmentation_array > 0.5, 1, 0)
    segmentation_array.astype(np.bool)

    return(uid, n_layer, segmentation_array)
