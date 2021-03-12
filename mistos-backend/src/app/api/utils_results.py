import numpy as np
from auto_tqdm import tqdm
import SimpleITK as sitk
import pandas as pd
from app.api.utils_transformations import binary_mask_to_multilabel
from typing import List

features = [
    "n_pixel",
    "sum_intensity"
]

n_features = len(features)


def calculate_measurement(image_array, labels_array):
    '''
    Function expects image array and labels array.
    features are sum pixel and number of pixels. Pixels are calculated over whole image stack!

    Parameters:

        - image_array(np.array): shape(z,c,y,x)
        - labels_array(np.array): shape(z,y,x) and type int. Every number > 0 corresponds to a label.
    '''
    n_channels = image_array.shape[1]
    # Use np.unique instead of max, since labels might be removed during labeling process, this would skip numbers.
    labels = np.unique(labels_array)
    # we reduce the label length since label 0 is empty
    measurement = np.zeros((len(labels)-1, n_channels, n_features))
    for n in range(n_channels):
        channel_array = image_array[:, n, ...]
        for i, label in tqdm(enumerate(labels)):
            if i == 0:
                continue
            label_array = np.where(labels_array == label, channel_array, 0)
            _sum_pixel = label_array.sum()
            _n_pixel = (label_array > 0).sum()
            measurement[i-1, n] = [_n_pixel, _sum_pixel]

    measurement_summary = {
        "n_labels": measurement.shape[0]
    }
    return measurement, measurement_summary


def get_feature_colnames(channel_name_list):
    colnames = []
    for c in channel_name_list:
        for f in features:
            colnames.append(f"{c}_{f}")
    return colnames

# replace: result_layer_uid with c_int_measurement + image
# replace


def calculate_measurement_df_for_result(experiment_group_uid: int, experiment_group_name: str, int_measurement, int_image):
    '''
    Helper method to format each result layers measurement into a measurement df for the result report.
    Returns pd.DataFrame

    Parameters:

        - experiment_group_uid(int): unique identifier of the experiment group
        - experiment_group_name(str): name of the experiment group
        - int_measurement
        - int_image
    '''

    measurement = int_measurement.measurement
    # Calculate BG
    # returns list of mean intensity per pixel values in order of channels#
    bg_mean_pixel_list = int_image.calculate_background()
    channel_name_list = int_image.metadata["custom_channel_names"]
    # Get Colnames
    colnames_features = get_feature_colnames(
        channel_name_list)
    colnames_background = [
        f"{c}_mean_background_per_pixel" for c in channel_name_list]
    measurement_reshaped = measurement.reshape(
        (measurement.shape[0], -1), order="C")
    # Here, pandas adds a index column
    measurement_df = pd.DataFrame(
        measurement_reshaped, columns=colnames_features)
    for i, bg_colname in enumerate(colnames_background):
        measurement_df[bg_colname] = bg_mean_pixel_list[i]
    measurement_df["n_z_slices"] = int_image.data.shape[0]

    measurement_df["image"] = f"{int_image.uid}_{int_image.metadata['original_filename']}"
    measurement_df["group"] = f"{experiment_group_uid}_{experiment_group_name}"
    return measurement_df


def generate_experiment_result_df(experiment_groups: List) -> pd.DataFrame:
    '''
    Helper method for IntExperiment to generate result Dataframe

    Parameters: 
        experiment_groups(List[app.api.classes_internal.IntExperimentGroup]): list of experiment groups for which the report should be created
    '''
    result_df_list = []
    for group in experiment_groups:
        result_df_list.append(group.get_experiment_result().data)

    assert len(result_df_list) > 0
    result_df = result_df_list[0]
    print(result_df)
    if len(result_df_list) > 1:
        for _result_df in result_df_list[1:]:
            # merge(_result_df, how = "outer")
            result_df = result_df.append(_result_df, ignore_index=True)
    return result_df


def staple_gte(segmentation_list):
    '''
    Expects list of label layers with (z,y,x))
    Labels will be binarized (if (label > 0) => 1 ? 0)
    Returns label layer of input shape according to staple probability and input threshold with individual labels.
    '''
    segmentation_list = [sitk.GetImageFromArray(
        np.where(segmentation > 0, 1, 0)) for segmentation in segmentation_list]
    gt_estimation = sitk.GetArrayFromImage(sitk.STAPLE(segmentation_list))
    gt_estimation = np.where(gt_estimation > 0.5, 1, 0)
    gt_estimation = binary_mask_to_multilabel(gt_estimation)[0]
    return gt_estimation
