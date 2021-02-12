import numpy as np
from pydantic import BaseModel, constr
from typing import List, Optional, Set, Any
from app import crud
from sqlalchemy.orm import Session

import app.api.classes_internal as c_int
import app.api.classes_com as c_com
import app.api.cfg_classes as cfg_classes
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
    layer_type: constr(regex = cfg_classes.layer_type_regex)

    def to_int_class(self):
        kwargs = self.dict()
        data = utils_import.load_label_layer_from_zarr(self.path)
        kwargs["data"] = data
        del kwargs["path"]

        return c_int.IntImageResultLayer(**kwargs)

    def to_com_class(self):
        kwargs = self.dict()
        kwargs["imageId"] = self.image_id
        kwargs["layerType"] = self.layer_type
        return c_com.ComImageResultLayer(**kwargs)

    def create_in_db(self):
        sql = crud.create_result_layer(self)
        self.uid = sql.id
        self.path = sql.path

    def delete(self):
        '''
        Calls crud method to Delete all associated measurements and the layer itself.
        '''
        print("dbimageresultlayer, delete")
        crud.delete_result_layer(self)

    def update_hint(self, new_hint):
        crud.update_result_layer_hint(self.uid, new_hint)

    def update_name(self, new_name):
        crud.update_result_layer_name(self.uid, new_name)

class DbResultMeasurement(BaseModel):
    uid: int
    name: str
    hint: str = ""
    image_id: int
    result_layer_id: int
    path: str = ""
    path_summary: str = ""

    def to_int_class(self):
        kwargs = self.dict()
        measurement = None
        kwargs["measurement"] = fsr.load_measurement(self.path)
        kwargs["measurement_summary"] = fsr.load_measurement_summary(self.path_summary)
        del kwargs["path"]
        del kwargs["path_summary"]
        return c_int.IntResultMeasurement(**kwargs)

    def create_in_db(self):
        sql = crud.create_result_measurement(self)
        self.uid = sql.id
        self.path = sql.path
        self.path_summary = sql.path_summary

    def to_com_class(self):
        kwargs = self.dict()
        kwargs["imageId"] = self.image_id
        kwargs["resultLayerId"] = self.result_layer_id
        kwargs["measurement_summary"] = fsr.load_measurement_summary(self.path_summary)
        del kwargs["path"]
        del kwargs["path_summary"]

        return c_com.ComResultMeasurement(**kwargs)

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

        if for_refresh == False:
            data, metadata = utils_import.load_zarr(kwargs["path_image"], kwargs["path_metadata"])
        else:
            metadata = fsr.load_metadata(self.path_metadata)

        image_result_layers = [image_result_layer.to_int_class() for image_result_layer in self.image_result_layers]

        del kwargs["path_metadata"]
        del kwargs["path_image"]

        kwargs["metadata"] = metadata
        if for_refresh == False:
            kwargs["data"] = data
        else: 
            kwargs["data"] = None
        kwargs["image_result_layers"] = image_result_layers
        kwargs["result_measurements"] = [measurement.to_int_class() for measurement in self.measurements]
 
        return c_int.IntImage(**kwargs)

    def to_com_class(self, for_refresh = False):
        kwargs = self.dict()
        kwargs["metadata"] = utils_import.load_metadata_only(self.path_metadata)
        kwargs["imageResultLayers"] = [image_result_layer.to_com_class() for image_result_layer in self.image_result_layers]
        kwargs["measurements"] = [measurement.to_com_class() for measurement in self.measurements]
        kwargs["seriesIndex"] = self.series_index
        kwargs["hasBgLayer"] = self.has_bg_layer
        kwargs["bgLayerId"] = self.bg_layer_id
        kwargs["tags"] = list(self.tags)

        return c_com.ComImage(**kwargs)

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

    def update_hint(self, new_hint):
        '''
        This function expects a new hint as string and calls crud.update_image_hint to update the image hint.
        '''
        crud.update_image_hint(self.uid, new_hint)

    def update_channel_names(self, channel_names):
        '''
        This function expects a new channel names as list of strings.
        opens metadata.json and edits custom_channel_names
        '''
        metadata = fsr.load_metadata(self.path_metadata)
        metadata["custom_channel_names"] = channel_names
        fsr.save_metadata(metadata, self.path_metadata)

    def delete_from_system(self):
        '''
        calls crud.delete_image and passed db_image object to delete all associated files and db entries
        '''
        crud.delete_image(self)

class DbExperimentGroup(BaseModel):
    uid: int
    name: str
    hint: str = ""
    experiment_id: int
    description: str = ""
    images: List[DbImage] = []
    result_layer_ids: List[int] = []
    measurement_ids: List[int] = []

    def to_int_class(self, for_refresh = False):
        kwargs = self.dict()
        images = [img.to_int_class() for img in self.images]
        kwargs["images"] = images
        int_experiment_group = c_int.IntExperimentGroup(**kwargs)
        return int_experiment_group

    def to_com_class(self):
        kwargs = self.dict()
        kwargs["experimentId"] = self.experiment_id
        kwargs["images"] = [i.to_com_class() for i in self.images]
        kwargs["resultLayerIds"] = self.result_layer_ids
        kwargs["measurementIds"] = self.measurement_ids

        return c_com.ComExperimentGroup(**kwargs)

    def create_in_db(self):
        sql_group = crud.create_experiment_group(self)
        self.uid = sql_group.id

    def add_image_by_uid(self, image_uid):
        db_image = crud.add_image_to_experiment_group(self, image_uid)
        return db_image.to_int_class()

    def remove_image_by_uid(self, uid):
        crud.remove_image_from_experiment_group(self, uid)

    def add_result_layer(self, uid):
        '''
        This function expects a layer uid.
        It retrieves the group's layer list and checks if another layer with of the same image is present in this experiment group. 
        If so, the other layer is removed first, then the current layer is added.
        '''
        new_db_result_layer = crud.read_result_layer_by_uid(uid)
        image_id = new_db_result_layer.image_id

        for current_result_layer_id in self.result_layer_ids:  
            current_layer = crud.read_result_layer_by_uid(current_result_layer_id)
            if current_layer.image_id == image_id:
                self.remove_result_layer(current_result_layer_id)

        crud.add_result_layer_to_experiment_group(self, uid)

    def add_measurement(self, uid):
        crud.add_measurement_to_experiment_group(self, uid)

    def update_name(self, new_name):
        crud.update_experiment_group_name(self.uid, new_name)

    def update_hint(self, new_hint):
        crud.update_experiment_group_hint(self.uid, new_hint)

    def update_description(self, new_description):
        crud.update_experiment_group_description(self.uid, new_description)

    def update_images(self, image_id_list):
        crud.update_experiment_group_images(self.uid, image_id_list)

    def remove_image(self, uid):
        '''
        Function expects an image id. Removes image from the group. Alse removes all result layers of this image from the group.
        '''
        crud.remove_image_from_experiment_group(self, uid)

        for current_result_layer_id in self.result_layer_ids:  
            current_layer = crud.read_result_layer_by_uid(current_result_layer_id)
            if current_layer.image_id == uid:
                self.remove_result_layer(current_result_layer_id) 

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
    experiment_group_id: int
    result_type: constr(regex = cfg_classes.result_type_regex)
    path: Optional[str] = ""

    def to_int_class(self):
        kwargs = self.dict()
        kwargs["data"] = fsr.load_result_df(self.path)
        
        return c_int.IntExperimentResult(**kwargs)

    def create_in_db(self):
        sql_result = crud.create_experiment_result(self)
        self.uid = sql_result.id
        self.path = sql_result.path

    def to_com_class(self):
        kwargs = self.dict()
        kwargs["experimentGroups"] = [g.uid for g in self.experiment_groups]
        kwargs["resultType"] = self.result_type

        return c_com.ComExperimentResult(**kwargs)

class DbExperiment(BaseModel):
    uid: int
    name: str
    hint: str
    description: str
    tags: Set[str] = set()
    experiment_groups: Optional[List[DbExperimentGroup]] = []

    def to_int_class(self):
        kwargs = self.dict()
        kwargs["experiment_groups"] = [group.to_int_class() for group in self.experiment_groups]
        return c_int.IntExperiment(**kwargs)

    def create_in_db(self):
        sql_experiment = crud.create_experiment(self)
        self.uid = sql_experiment.id

    def to_com_class(self):
        kwargs = self.dict()
        kwargs["experimentGroups"] = [group.to_com_class() for group in self.experiment_groups]
        kwargs["tags"] = list(self.tags)

        return c_com.ComExperiment(**kwargs)

    def update_name(self, new_name):
        crud.update_experiment_name(self.uid, new_name)

    def update_hint(self, new_hint):
        crud.update_experiment_hint(self.uid, new_hint)

    def update_description(self, new_description):
        crud.update_experiment_description(self.uid, new_description)

    def update_tags(self, new_tags):
        pass

    def delete_experiment_group(self, experiment_group_id):
        crud.delete_experiment_group_by_id(experiment_group_id)

    def delete(self):
        '''
        Function deletes the experiment from the db
        '''
        crud.delete_experiment_by_id(self.uid)

class DbClassifier(BaseModel):
    uid: int
    name: str = ""
    clf_type: constr(regex = cfg_classes.classifier_type_regex)
    path_clf: str = "" 
    path_test_train: str = ""
    params: dict = {}
    metrics: dict = {}
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

    def to_com_class(self):
        kwargs = self.dict()
        kwargs["tags"] = list(self.tags)
        kwargs["clfType"] = self.clf_type

        return c_com.ComClassifier(**kwargs)

    def create_in_db(self):
        sql_classifier = crud.create_classifier(self)
        self.uid = sql_classifier.id
        self.path_clf = sql_classifier.path_clf
        self.path_test_train = sql_classifier.path_test_train

