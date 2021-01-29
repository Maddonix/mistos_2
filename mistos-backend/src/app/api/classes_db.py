import numpy as np
from pydantic import BaseModel, constr
from typing import List, Optional, Set, Any
from app import crud
from sqlalchemy.orm import Session

import app.api.classes_internal as c_int
import app.api.utils_classes as utils_classes
import app.api.utils_paths as utils_paths
from app import fileserver_requests as fsr
from app.api import utils_import
from app import crud

class DbImageResultLayer(BaseModel):
    uid: int
    name: str
    hint: str
    path: Optional[str]
    image_id: int
    layer_type: constr(regex = utils_classes.layer_type_regex)

    def to_int_class(self):
        kwargs = self.dict()
        data = utils_import.load_label_layer_from_zarr(self.path)
        kwargs["data"] = data
        del kwargs["path"]

        return c_int.IntImageResultLayer(**kwargs)

    def create_in_db(self):
        sql = crud.create_result_layer(self)
        self.uid = sql.id
        self.path = sql.path

    def delete(self):
        print("dbimageresultlayer, delete")
        crud.delete_result_layer(self)

class DbResultMeasurement(BaseModel):
    uid: int
    name: str
    hint: str = ""
    image_id: int
    result_layer_id: int
    path: str = ""

    def to_int_class(self):
        kwargs = self.dict()
        measurement = None
        kwargs["measurement"] = fsr.load_measurement(self.path)
        del kwargs["path"]
        return c_int.IntResultMeasurement(**kwargs)

    def create_in_db(self):
        sql = crud.create_result_measurement(self)
        self.uid = sql.id
        self.path = sql.path

class DbImage(BaseModel):
    uid: int
    series_index: int
    name: str
    hint: str = ""
    path_metadata: Optional[str]
    path_image: Optional[str]
    has_bg_layer: bool = False
    bg_layer_id: Optional[int]
    image_result_layers: List[DbImageResultLayer] = []
    measurements: List[DbResultMeasurement] = []
    tags: Set[str] = []

    def to_int_class(self, for_refresh = False):
        kwargs = self.dict()

        metadata = {"dummy": "dict"} # Read metadata from path
        data = np.zeros((4,3,100,100)) # Read zarr from path
        if for_refresh == False:
            data, metadata = utils_import.load_zarr(kwargs["path_image"], kwargs["path_metadata"])
        image_result_layers = [image_result_layer.to_int_class() for image_result_layer in self.image_result_layers]

        del kwargs["path_metadata"]
        del kwargs["path_image"]
        kwargs["metadata"] = metadata
        if for_refresh == False:
            kwargs["data"] = data
        else: 
            kwargs["data"] = None
        kwargs["image_result_layers"] = image_result_layers
 
        return c_int.IntImage(**kwargs)

    def set_bg_false(self):
        crud.update_image_bg_false(self.uid)

    def set_bg_true(self, layer_uid):
        crud.update_image_bg_true(self.uid, layer_uid)

    def create_in_db(self):
        sql_image = crud.create_image(self)
        self.uid = sql_image.id
        self.path_image = sql_image.path_image
        self.path_metadata = sql_image.path_metadata

    def refresh_from_db(self):
        updated_db_image = crud.read_image_by_uid(self.uid, for_refresh = True)
        return updated_db_image

class DbExperimentGroup(BaseModel):
    uid: int
    name: str
    hint: str = ""
    experiment_id: int
    description: Optional[str] = ""
    images: Optional[List[DbImage]] = []
    result_layer_ids: List[int] = []
    measurement_ids: List[int] = []

    def to_int_class(self, for_refresh = False):
        kwargs = self.dict()
        images = [img.to_int_class() for img in self.images]
        kwargs["images"] = images
        int_experiment_group = c_int.IntExperimentGroup(**kwargs)
        return int_experiment_group

    def create_in_db(self):
        sql_group = crud.create_experiment_group(self)
        self.uid = sql_group.id

    def add_image_by_uid(self, image_uid):
        db_image = crud.add_image_to_experiment_group(self, image_uid)
        return db_image.to_int_class()

    def remove_image_by_uid(self, uid):
        crud.remove_image_from_experiment_group(self, uid)

    def add_result_layer(self, uid):
        crud.add_result_layer_to_experiment_group(self, uid)

    def add_measurement(self, uid):
        crud.add_measurement_to_experiment_group(self, uid)

    def remove_image(self, uid):
        crud.remove_image_from_experiment_group(self, uid)

    def remove_result_layer(self, uid):
        crud.remove_result_layer_from_experiment_group(self, uid)

    def remove_measurement(self, uid):
        crud.remove_measurement_from_experiment_group(self, uid)

    def refresh_from_db(self):
        updated_info = crud.read_experiment_group_by_uid(self.uid, for_refresh = True)
        return updated_info

class DbExperimentResult(BaseModel):
    uid: int
    name: Optional[str] = ""
    hint: Optional[str] = ""
    description: Optional[str] = ""
    experiment_groups: Optional[List[DbExperimentGroup]] = []
    result_type: constr(regex = utils_classes.result_type_regex)
    path: Optional[str] = ""

    def to_int_class(self):
        pass

    def create_in_db(self):
        sql_result = crud.create_experiment_result(self)
        self.uid = sql_result.id
        self.path = sql_result.path

class DbExperiment(BaseModel):
    uid: int
    name: str
    hint: str
    description: str
    tags: Set[str] = set()
    experiment_groups: Optional[List[DbExperimentGroup]] = []

    def to_int_class(self):
        pass

    def create_in_db(self):
        sql_experiment = crud.create_experiment(self)
        self.uid = sql_experiment.id

class DbClassifier(BaseModel):
    uid: int
    name: str = ""
    clf_type: constr(regex = utils_classes.classifier_type_regex)
    path_clf: str = "" 
    path_test_train: str = ""
    params: Optional[dict]
    metrics: Optional[dict]
    tags: set = set()

    def to_int_class(self):
        kwargs = self.dict()
        clf = fsr.load_classifier(self.path_clf)
        test_train_data = fsr.load_classifier_test_train(self.path_test_train)

        kwargs["test_train_data"] = test_train_data
        kwargs["classifier"] = clf

        del kwargs["path_clf"]
        del kwargs["path_test_train"]

        return c_int.IntClassifier(**kwargs)

    def create_in_db(self):
        sql_classifier = crud.create_classifier(self)
        self.uid = sql_classifier.id
        self.path_clf = sql_classifier.path_clf
        self.path_test_train = sql_classifier.path_test_train

