from deepflash2.learner import EnsembleLearner, get_files, Path
from app import crud
import pathlib
import numpy as np
from app.api import classes_internal as c_int, utils_transformations

def predict_image_list(classifier_id, image_id_list, use_tta, transform_to_multilabel = True):
    '''
    Predict a list of images.

    keyword arguments:
    image_id_list -- list of integers, integers must be valid image uids
    classifier_id -- integer, must be valid classifier uid; classifier must be of type "deepflash_model"
    use_tta -- boolean, if true tta prediction is used. Image will be predicted in multiple orientations, consensus is returned. Takes significantly longer, yiels more reliable results
    '''
    # Read image paths
    image_path_list = [crud.read_db_image_by_uid(image_id).path_image for image_id in image_id_list]
    image_path_list = [pathlib.Path(path) for path in image_path_list]
    # Read classifier path
    classifier = crud.read_classifier_by_uid(classifier_id)
    assert classifier.clf_type == "deepflash_model"
    classifier_path = pathlib.Path(classifier.classifier)
    
    # Create EnsembleLearner and read model
    el = EnsembleLearner(files=image_path_list)
    el.get_models(classifier_path)

    # Pass image file paths to ensemble learner and predict images
    el.get_ensemble_results(image_path_list, use_tta = use_tta)

    for path in el.df_ens["res_path"]:
        path = pathlib.Path(path)
        image_id, segmentation = get_segmentation_from_path(path)

        # DeepFlash provides 2d segmentation only right now, therefore we have to change the dimension
        int_image = crud.read_image_by_uid(image_id)
        print(segmentation.shape)
        print(int_image.data.shape)
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
            segmentation = utils_transformations.binary_mask_to_multilabel(segmentation)[0]

        # Create new Result Layer
        result_layer = c_int.IntImageResultLayer(
            uid = -1,
            name = f"df_seg_{classifier.uid}_{classifier.name}",
            hint = f"Segmentation was created using DeepFlash2 (model: {classifier.name}, [ID: {classifier.uid}]",
            image_id = image_id,
            layer_type = "labels",
            data = segmentation
        )

        result_layer.on_init()
        print(result_layer)

        # Measure Mask in image
        int_image.refresh_from_db()
        int_image.measure_mask_in_image(result_layer.uid)

        

    # delete temp files
    el.clear_tmp()


def get_segmentation_from_path(path):
    '''
    takes path as pathlib.path and returns a tupple containing id and segmentation array with shape (z,y,x)

    returns: (uid, array) 
    '''
    uid = int(path.as_posix().split("/")[-1].split(".")[0])
    segmentation_array = np.load(path)["seg"] 
    segmentation_array = np.where(segmentation_array>0.5, 1, 0)
    segmentation_array.astype(np.bool)

    return(uid,segmentation_array)