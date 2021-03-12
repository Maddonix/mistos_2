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

export_types = [
    "images",  # Images as .tiff will be included in export
    "masks",  # Masks will be included in export
    "rescaled",  # All masks and images will be exported in original form and rescaled
    # All masks and images will be exported in original form and as max_z_projections
    "z_projection",
    "images_single_channel",  # Greyscale images of specified channels will be exported
    "masks_binary",  # binary masks_will be exported
    "masks_png",  # masks will be exported as .png
    "rois",  # masks will be exported as ImageJ Rois
]


result_type_regex = f"^({'|'.join(result_types)}$)"
layer_type_regex = f"^({'|'.join(layer_types)}$)"
classifier_type_regex = f"^({'|'.join(classifier_types)}$)"
