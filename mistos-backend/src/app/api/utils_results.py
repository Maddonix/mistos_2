import numpy as np
from auto_tqdm import tqdm
import SimpleITK as sitk

features = [
    "n_pixel",
    "sum_intensity"
]

n_features = len(features)


def calculate_measurement(image_array, labels_array):
    '''
    Function expects image array and labels array.
    features are sum pixel and number of pixels. Pixels are calculated over whole image stack!

    keyword arguments:
    image_array -- np.array of shape(z,c,y,x)
    labels_array -- np.array of shape(z,y,x) and type int. Every number corresponds to a label.
    '''
    n_channels = image_array.shape[1]
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


def staple_gte(segmentation_list):
    '''
    Expects list of label layers (shape (z,y,x))
    Labels will be binarized (if (label > 0) => 1 ? 0)
    Returns binarized label layer of input shape according to staple probability and input threshold.
    '''
    segmentation_list = [sitk.GetImageFromArray(
        np.where(segmentation > 0, 1, 0)) for segmentation in segmentation_list]
    gt_estimation = sitk.GetArrayFromImage(sitk.STAPLE(segmentation_list))
    gt_estimation = np.where(gt_estimation > 0.5, 1, 0)
    return gt_estimation
