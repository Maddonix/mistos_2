import numpy as np

from app.api import classes_internal as c_int
from app.api import classes_db as c_db
from app.api import classes_com as c_com


dummy_image = c_int.IntImage(
    uid = -1,
    name = "dummy_image",
    series_index = 0,
    metadata = {"dummy": "metadata"},
    hint = "dummy_hint",
    tags = set(["dummy"]),
    data = np.zeros((4,3,100,100))
)

dummy_result_layer = c_int.IntImageResultLayer(
    uid = -1,
    name = "dummy_result_layer",
    hint = "dummy_hint",
    image_id = -1,
    layer_type = "labels",
    data = np.zeros((4,3,100,100))
)

dummy_result_measurement = c_int.IntResultMeasurement(
    uid = -1,
    name = "dummy_measurement",
    hint = "dummy_hint",
    image_id = -1,
    resultLayer_id = -1,
    channel = 0,
    measurement = {"dummy": "measurements"}
)

dummy_experiment_group = c_int.IntExperimentGroup(
    uid = -1,
    experiment_id = -1,
    name = "dummy_experiment group",
    hint = "dummy_hint",
    description = "dummy_description",
    images = [dummy_image, dummy_image]
)

dummy_result = c_int.IntExperimentResult(
    uid = -1,
    description = "asdasd",
    experiment_groups = [],
    active_image_ids = [],
    active_image_result_layer_ids = [],
    result_type = "measure"
)

dummy_experiment = c_int.IntExperiment(
    uid = -1,
    name = "dummy_experiment",
    hint = "dummy_hint",
    description = "dummy_description",
    tags = set(["dummy", "experiment"]),
    experiment_groups = [],
    active_image_ids = [],
    active_image_result_layer_ids = [],
    experiment_result = dummy_result
)