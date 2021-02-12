import numpy as np
from auto_tqdm import tqdm

features = [
    "n_pixel",
    "sum_intensity"
]

n_features = len(features)


def calculate_measurement(image_array, labels_array):
    '''
    Function expects image array and labels array.

    keyword arguments:
    image_array -- np.array of shape(z,c,y,x)
    labels_array -- np.array of shape(z,y,x) and type int. Every number corresponds to a label.
    '''
    n_channels = image_array.shape[1]
    labels = np.unique(labels_array)

    measurement = np.zeros((len(labels), n_channels, n_features))

    np.zeros((len(labels), n_channels, n_features))
    for n in range(n_channels):
        channel_array = image_array[:,n,...]
        for i, label in tqdm(enumerate(labels)):
            label_array = np.where(labels_array == label, channel_array, 0)
            _sum_pixel = label_array.sum()
            _n_pixel = (label_array>0).sum()
            measurement[i, n] = [_n_pixel, _sum_pixel]

    measurement_summary = {
        "n_labels": measurement.shape[0]
    }

    return measurement, measurement_summary

def get_feature_colnames(channel_name_list):
    colnames=[]
    for c in channel_name_list:
        for f in features:
            colnames.append(f"{c}_{f}")

    return colnames