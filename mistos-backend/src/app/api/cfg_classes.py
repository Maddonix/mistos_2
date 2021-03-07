from collections import namedtuple


channel_measurement_tuple = namedtuple("channel_measurement", [
                                       "channel", "sum", "mean", "applied_bg_correction_per_pixel"])

result_types = [
    "segmentation",
    "count",
    "measure"
]

layer_types = [
    "labels",
    "points",
    "shapes",
    "image"
]

classifier_types = [
    "rf_segmentation",
    "deepflash_model"
]

result_type_regex = f"^({'|'.join(result_types)}$)"
layer_type_regex = f"^({'|'.join(layer_types)}$)"
classifier_type_regex = f"^({'|'.join(classifier_types)}$)"
