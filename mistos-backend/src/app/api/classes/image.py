import copy
from os import name
import warnings
import xml
from pathlib import Path
from typing import Any, List, Optional, Set

import numpy as np
from app import crud
from app import fileserver_requests as fsr
from app.api import utils_import, utils_paths, utils_results
from app.api.classes.image_result_layer import (DbImageResultLayer,
                                                IntImageResultLayer)
from app.api.classes.result_measurement import (DbResultMeasurement,
                                                IntResultMeasurement)
from app.api.classes_com import ComImage
from app.api.dependencies import check_sess
from pydantic import BaseModel, constr
from pathlib import Path


class DbImage(BaseModel):
    '''
    A class to handle database and file storage of Images

    Attributes
    ----------
    uid : int
        the objects unique identifier
    series_index : int
        index of image if multiple images were imported in a single file
    name : str 
        the objects name
    hint : str = ""
        empty string by default. brief description of the object
    has_bg_layer: bool = False
        indicator if image has an associated background layer.
    bg_layer_id: int, optional
        None if no associated background layer, otherwise id of the background layer.
    path_metadata: pathlib.Path, optional
        path to the images metadata ".json". Automatically generated as image is saved to database.
    path_image: pathlib.Path, optional
        path to the images array ".zarr" folder. Automatically generated as image is saved to database.
    image_result_layers: List[DbImageResultLayer] = []
        emtpy list by default. List of all associated DbImageResultLayer objects
    measurements: List[DbResultMeasurement] = []
        emtpy list by default. List of all associated DbResultMeasurement objects
    tags: Set[str] = []
        set of string keywords to easily categorize objects in frontend.

    Methods
    -------
    to_int_class()->app.api.classes_internal.IntImage:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComImage:
        returns object as com_class. 
    set_bg_false(sess = None)
        sets "has_bg_layer" property to False in db.
    set_bg_true(layer_uid: int, sess = None)
        sets "has_bg_layer" property to True in db. sets bg_layer_id to given value.
    create_in_db(sess = None):
        creates object in database, updates objects path and uid attributes accordingly. Uses default session if none is passed.
    refresh_from_db() -> DbImage
        Fetches image from database and returns DbImage object.
    update_hint(new_hint: str, sess = None):
        updates objects hint in database. Uses default session if none is passed.
    update_channel_names(channel_names: List[str])
        edits "custom_channel_names" attribute of image in it's metadata.json    
    delete_from_system(sess = None):
        deletes object in database and file storage. Uses default session if none is passed.
    '''

    uid: int
    series_index: int
    name: str
    hint: str = ""
    has_bg_layer: bool = False
    bg_layer_id: Optional[int]
    path_metadata: Optional[Path]
    path_image: Optional[Path]
    image_result_layers: List[DbImageResultLayer] = []
    measurements: List[DbResultMeasurement] = []
    tags: Set[str] = []

    def to_int_class(self, for_refresh=False):
        '''
        Returns object as int class.

        Parameters:
            - for_refresh(bool = False): If True, image array is not reloaded from file storage.
        '''
        kwargs = self.dict()
        # Only load the full image if not already loaded
        if for_refresh == False:
            data = fsr.load_zarr(kwargs["path_image"])
            kwargs["data"] = data
        else:
            kwargs["data"] = None
        metadata = fsr.load_json(self.path_metadata)
        metadata_omexml_path = utils_paths.make_metadata_xml_path_from_json_path(
            self.path_metadata)
        kwargs["metadata_omexml"] = fsr.load_metadata_xml(metadata_omexml_path)
        del kwargs["path_metadata"]
        del kwargs["path_image"]
        kwargs["metadata"] = metadata
        kwargs["image_result_layers"] = [image_result_layer.to_int_class()
                                         for image_result_layer in self.image_result_layers]
        kwargs["result_measurements"] = [measurement.to_int_class()
                                         for measurement in self.measurements]
        return IntImage(**kwargs)

    def to_com_class(self):
        '''
        Returns obect as com class.
        '''
        kwargs = self.dict()
        kwargs["metadata"] = utils_import.load_metadata_only(
            self.path_metadata)
        kwargs["imageResultLayers"] = [image_result_layer.to_com_class()
                                       for image_result_layer in self.image_result_layers]
        kwargs["measurements"] = [measurement.to_com_class()
                                  for measurement in self.measurements]
        kwargs["seriesIndex"] = self.series_index
        kwargs["hasBgLayer"] = self.has_bg_layer
        kwargs["bgLayerId"] = self.bg_layer_id
        kwargs["tags"] = list(self.tags)
        return ComImage(**kwargs)

    def set_bg_false(self, sess=None):
        '''
        Sets imagaes has_bg_layer property to False in database.

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.update_image_bg_false(self.uid, sess)

    def set_bg_true(self, layer_uid: int, sess=None):
        '''
        Sets images bg_layer_id property to given value.

        Parameters:

            - layer_uid(int): uid of result layer to be used as background layer.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.update_image_bg_true(self.uid, layer_uid, sess)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Paths and id are generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        sql_image = crud.create_image(self, sess)
        self.uid = sql_image.id
        self.path_image = Path(sql_image.path_image)
        self.path_metadata = Path(sql_image.path_metadata)

    def refresh_from_db(self, sess=None):
        '''
        Refreshes object image from db.

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        updated_db_image = crud.read_image_by_uid(
            self.uid, sess, for_refresh=True)
        return updated_db_image

    def update_hint(self, new_hint: str, sess=None):
        '''
        This function expects a new hint as string and calls crud.update_image_hint to update the image hint.

        Parameters:

            - new_hint(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_image_hint(self.uid, new_hint, sess)

    def update_channel_names(self, channel_names: List[str]):
        '''
        This function expects a new channel names as list of strings. opens metadata.json and edits custom_channel_names

        Parameters:

            - channel_names(List[str]): List of strings to be saved as channel names.
        '''
        metadata = fsr.load_json(self.path_metadata)
        metadata["custom_channel_names"] = channel_names
        fsr.save_metadata(metadata, self.path_metadata)

    def delete_from_system(self, sess=None):
        '''
        calls crud.delete_image and passed db_image object to delete all associated files and db entries

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.delete_image(self, sess)


class IntImage(BaseModel):
    '''
    A class to handle calculations and other internal operations with images.

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    series_index : int
        if multiple images are imported via one file (image series), the index of the image is stored here
    metadata : dict
        reduced metadata for easy use within mistos. As created by app.api.utils_import.acquire_metadata_dict (creates metadata dict for whole series)
        Series metadatadict is passed into IntImage.on_init(). Thereafter, only image's metadata will be saved to .json and loaded.
    hint : str, optional
        empty string by default. brief description of the object
    experiment_ids: List[int]
        empty list by default. List of experiments_group ids which use the image.
    image_result_layers : List[IntImageResultLayer]
        empty list by default. List of all associated IntImageResultLayer objects.
    result_measurements : List[IntResultMeasurement]
        empty list by default. List of all associated IntResultMeasurement objects
    tags : Set[str]:
        empty set by default. Set of keywords to work with in the frontend
    data : Any   ___TO BE DONE: add custom field type___
        array of shape (z,c,y,x) in which the image is stored. Is loaded from .zarr files, most numpy operations work, some may cause trouble.
    metadata_omexml : Any
        original metadata xml data as read by bioformats import when image was imported
    has_bg_layer : bool
        False by default. Indicates if image as layer selected as background_layer.
    bg_layer_id : int, optional
        None if no bg_layer selected, otherwise it holds the bg_layer_id 

    Methods
    -------
    on_init():
        Initializes object. Object is saved in database and file storage
    get_thumbnail_path():
        Helper function which returns path to the thumbnail on fileserver.
    get_image_scaling():
        Returns dimensions normalized scales in array with shape (z,y,x) or None.
    to_db_class() -> app.api.classes_db.DbImage:
        Returns object as DbImage object.
    set_bg_false():
        Helper function to set has_bg_layer to False and bg_layer_id to None.
    set_bg_true(image_layer: app.api.classes_int.IntImageResultLayer):
        Method to set layer as background layer
    select_channel(channel: int) -> np.array:
        Helper method expects channel index. Returns deep copy of channel with shape (z,y,x).
    select_result_layer(uid: int) -> app.api.classes_internal.IntResultLayer | None:
        Returns layer with corresponding id, returns None if id is not found in self.image_result_layers
    calculate_background() -> List:
        Returns list of length n_channels. List holds the mean pixel values for each channel if background layer is defined and zeros if no background layer is defined.
    measure_mask_in_image(layer_id: int) -> app.api.classes_int.IntMeasurementResult:
        Returns measurement object for given result layer and saves it to db and file storage.
    get_classifiers(clf_type: str) -> dict:
        Fetches all saved classifiers from db, filters for type and returns dictionary of format {"UID_NAME": UID}
    refresh_from_db():
        Fetches data of this image from db and updates the objects attributes.
    delete_result_layer(layer_id: int):
        Deletes the layer from database, file storage and the image. If layer was background_layer, corresponding attributes are reset.
    estimate_ground_truth_layer(layer_id_list: List[int], suffix: str):
        Fetches given layers and uses SimpleITKs STAPLE algorithm to estimate ground truth. 
        Resulting layer will be initialized as IntResultLayer.  
    add_layer_from_roi(path)
    add_layer_from_mask(path)
    '''
    uid: int
    name: str
    series_index: int
    metadata: dict
    hint: Optional[str] = ""
    experiment_ids: List[int] = []
    image_result_layers: List[IntImageResultLayer] = []
    result_measurements: List[IntResultMeasurement] = []
    tags: Set[str] = set()
    data: Any
    metadata_omexml: Any
    has_bg_layer: bool = False
    bg_layer_id: Optional[int]

    def on_init(self):
        '''
        Method to initialize the object. Handles image as new image if "uid" == -1 and as imported Mistos image if "uid" == -2.
        Creates image in database which generates path and id. 
        '''
        if self.uid == -1:
            db_image = self.to_db_class()
            db_image.create_in_db()
            self.uid = db_image.uid
            original_filename = self.metadata["original_filename"]
            self.metadata = self.metadata["images"][self.series_index]
            self.metadata["original_filename"] = original_filename
            # save zarr
            fsr.save_zarr(self.data, db_image.path_image)
            # save metadata dict
            fsr.save_json(self.metadata, db_image.path_metadata)
            # save metadata xml
            path_xml = utils_paths.make_metadata_xml_path_from_json_path(
                db_image.path_metadata)
            metadata_string = self.metadata_omexml.to_xml(encoding="utf-8")
            metadata_string = xml.dom.minidom.parseString(
                metadata_string).toprettyxml(indent="\t")
            fsr.save_metadata_xml(metadata_string, path_xml)

        elif self.uid == -2:
            db_image = self.to_db_class()
            db_image.create_in_db()
            self.uid = db_image.uid
            print(f"Importing archived Mistos image with id {self.uid}")
            fsr.save_zarr(self.data, db_image.path_image)
            fsr.save_json(self.metadata, db_image.path_metadata)
            path_xml = utils_paths.make_metadata_xml_path_from_json_path(
                db_image.path_metadata)
            # metadata_string = self.metadata_omexml.to_xml(encoding="utf-8")
            metadata_omexml = self.metadata_omexml.toprettyxml(indent="\t")
            fsr.save_metadata_xml(metadata_omexml, path_xml)

        # save thumbnail
        thumbnail = utils_import.generate_thumbnail(self.data)
        thumbnail_path = self.get_thumbnail_path()
        fsr.save_thumbnail(thumbnail, thumbnail_path)

    def get_thumbnail_path(self):
        ''' 
        Helper function which returns path to the thumbnail on fileserver. 
        Gets gets fileserver path and joins with return value from utils_paths.make_thumbnail_path
        Returns path as pathlib.Path
        '''
        return utils_paths.fileserver.joinpath(utils_paths.make_thumbnail_path(self.uid))

    def get_image_scaling(self):
        '''
        Reads pixel dimensions and returns relative dimensions.
        Returns dimensions normalized scales in array with shape (z,y,x) or None if no scaling information was provided in metadata.
        '''
        x = self.metadata['pixel_size_physical_x']
        y = self.metadata['pixel_size_physical_y']
        z = self.metadata['pixel_size_physical_z']
        n_z = self.metadata['pixel_size_z']
        if n_z > 1:
            dims = np.array([z, y, x])
            dims = dims/dims.max()
        elif n_z == 1:
            dims = np.array([y, x])
            dims = dims/dims.max()
        else:
            dims = None
            print("Couldn't calculate scaling from metadata, defaulting to None")

        return dims

    def to_db_class(self):
        '''
        Transforms internal class representation to db class representation.
        '''
        db_image_result_layers = [result_layer.to_db_class()
                                  for result_layer in self.image_result_layers]
        db_result_measurements = [measurement.to_db_class()
                                  for measurement in self.result_measurements]
        db_image = DbImage(
            uid=self.uid,
            series_index=self.series_index,
            name=self.name,
            hint=self.hint,
            path_metadata=None,
            path_image=None,
            has_bg_layer=self.has_bg_layer,
            bg_layer_id=self.bg_layer_id,
            experiment_ids=self.experiment_ids,
            image_result_layers=db_image_result_layers,
            result_measurements=db_result_measurements,
            tags=self.tags
        )
        return db_image

    def set_bg_false(self):
        '''
        Helper function to set has_bg_layer to False and bg_layer_id to None.
        Attribute is changed in db, then object attributes are reloaded from db.
        '''
        db_image = self.to_db_class()
        db_image.set_bg_false()
        self.refresh_from_db()

    def set_bg_true(self, image_layer: IntImageResultLayer):
        '''
        Method to set layer as background layer.

        Parameters:

            - image_layer(app.api.classes_int.IntImageImageResultLayer): Layer to be selected as background layer.
        '''
        layer_uid = image_layer.uid
        db_image = self.to_db_class()
        db_image.set_bg_true(layer_uid)
        self.refresh_from_db()

    def select_channel(self, channel: int):
        '''
        Helper method expects channel index.
        Returns deep copy of channel with shape (z,y,x).

        Parameters: 

            - channel(int): index of channel to be selected.
        '''
        channel_data = copy.deepcopy(self.data[:, channel, ...])[
            :, np.newaxis, ...]
        return channel_data

    def select_result_layer(self, uid: int):

        layers = [_ for _ in self.image_result_layers if _.uid == uid]
        if len(layers) > 0:
            return layers[0]
        else:
            warnings.warn(
                f"IntImage.select channel could not select layer with id {uid}.\nThis image has the associated layers \n{layers}",
                UserWarning)
            return None

    def calculate_background(self):
        '''
        Expects the bg_uid to belong to a result layer of this image.
        Result layer will be turned to binary, assuming all labels > 0 to be background.
        Returns list of length n_channel with mean intensity of measured pixels.
        '''
        if self.has_bg_layer:
            bg_uid = self.bg_layer_id
            bg_layer = self.select_result_layer(bg_uid)
            bg_mask = bg_layer.data
        else:
            bg_mask = np.zeros((
                self.data.shape[0],
                self.data.shape[2],
                self.data.shape[3]
            ))
        if bg_mask.max() < 2:
            bg_mask = np.where(bg_mask > 0, 1, 0)
        n_pixel = bg_mask.sum()
        n_channel = self.data.shape[1]
        mean_pixel = []
        for n in range(n_channel):
            channel_data = self.select_channel(n)
            selection = np.where(bg_mask, channel_data, 0)
            _mean = selection.sum()/n_pixel
            mean_pixel.append(_mean)

        return mean_pixel

    def measure_mask_in_image(self, layer_id: int):
        '''
        Method to measure mask and save result as ResultMeasurement. Creates measurement object and initializes it (save to db and file storage)
        Returns IntResultMeasurement object:
        measurement.measurement has shape: (n_labels, n_channel, n_features), n_features == 2 (n_pixels, sum_pixels)

        Parameters:

            - layer_id(int): uid of the layer to be measured
        '''
        image_array = self.data
        layer = self.select_result_layer(layer_id)
        measurement, measurement_summary = utils_results.calculate_measurement(
            image_array, layer.data)
        measurement_result = IntResultMeasurement(
            uid=-1,
            name=utils_paths.make_measurement_name(self.name, layer.name),
            hint="",
            image_id=self.uid,
            result_layer_id=layer.uid,
            measurement=measurement,
            measurement_summary=measurement_summary
        )
        measurement_result.on_init()
        self.refresh_from_db()

        return measurement_result

    def get_classifiers(self, clf_type: str):
        '''
        Loads all classifiers of given type from database.
        Returns dictionary of format {"UID_NAME": UID}. Mainly for use in napari viewer.

        Parameters:

            - clf_type(str): Valid classifier type, for available types see app.api.cfg_classes.classifier_types.
        '''
        # Fetches dict in form {name: id}
        clf_dict = crud.read_classifier_dict_by_type(clf_type)
        if clf_dict == {}:
            clf_dict["No classifers found"] = None
        return clf_dict

    def refresh_from_db(self):
        '''
        Requests current information from db and updates the object's attributes accordingly.
        Does not reload image data again
        '''
        db_image = self.to_db_class()
        updated_info = db_image.refresh_from_db()
        self.name = updated_info.name
        self.hint = updated_info.hint
        self.experiment_ids = updated_info.experiment_ids
        self.image_result_layers = updated_info.image_result_layers
        self.result_measurements = updated_info.result_measurements
        self.tags = updated_info.tags
        self.has_bg_layer = updated_info.has_bg_layer
        self.bg_layer_id = updated_info.bg_layer_id

    def delete_result_layer(self, layer_id: int):
        '''
        Method to delete a result layer by uid. 
        If result layer is selected as background layer, the attributes "has_bg_layer" and "bg_layer_id" are set to False and None.

        Parameters:

            - layer_id(int): Id of result layer to be deleted.
        '''
        layer = self.select_result_layer(layer_id)
        if layer_id == self.bg_layer_id:
            self.set_bg_false()
        layer.delete()
        self.refresh_from_db()

    def estimate_ground_truth_layer(self, layer_id_list: List[int], suffix: str = None):
        '''
        Method to estimate ground truth from multiple layers with by SimpleITK's STAPLE probabilities.
        For ground truth estimation layer will be binarized, all labels > 0 will be unified and represented as foreground (==1) for calculation.
        Saves label layer to image, database and file storage.

        Parameters:

            - layer_id_list(List[int]): List of layer ids to be used for ground truth estimation. Must belong to this image.
            - suffix(str): will be appended to layer name.
        '''
        if suffix == None:
            suffix = ""
        else:
            suffix = "_" + suffix
        label_array_list = [crud.read_result_layer_by_uid(
            layer_id).to_int_class().data for layer_id in layer_id_list]
        ground_truth_estimation_array = utils_results.staple_gte(
            label_array_list)
        hint = f"Following Label Layers were used to estimate the ground truth: {layer_id_list}"
        int_result_layer = IntImageResultLayer(
            uid=-1,
            name=f"ground_truth_estimation{suffix}",
            hint=hint,
            image_id=self.uid,
            layer_type="labels",
            data=ground_truth_estimation_array
        )
        int_result_layer.on_init()
        self.refresh_from_db()
        self.measure_mask_in_image(int_result_layer.uid)

    def add_layer_from_roi(self, path: Path):
        mask = utils_import.read_roi(path, self.data.shape)
        int_result_layer = IntImageResultLayer(
            uid=-1,
            name=f"{path.name}",
            hint="imported maks",
            image_id=self.uid,
            layer_type="labels",
            data=mask
        )
        int_result_layer.on_init()
        self.refresh_from_db()
        self.measure_mask_in_image(int_result_layer.uid)

    def add_layer_from_mask(self, path: Path):
        mask = utils_import.read_mask(path)
        if type(mask) == type(None):
            warnings.warn("Image could not be read!")
            return None
        else:
            image_shape = self.data.shape
            if mask.shape == (image_shape[0], image_shape[-2], image_shape[-1]):
                int_result_layer = IntImageResultLayer(
                    uid=-1,
                    name=f"{path.name}",
                    hint="imported mask",
                    image_id=self.uid,
                    layer_type="labels",
                    data=mask
                )
                int_result_layer.on_init()
                self.refresh_from_db()
                self.measure_mask_in_image(int_result_layer.uid)
            elif mask.shape == (1, image_shape[-2], image_shape[-1]):
                _mask = np.zeros((image_shape[0], image_shape[-2], image_shape[-1]))
                _mask[:,...] = mask
                int_result_layer = IntImageResultLayer(
                    uid=-1,
                    name=f"{path.name}",
                    hint="imported mask",
                    image_id=self.uid,
                    layer_type="labels",
                    data=_mask
                )
                int_result_layer.on_init()
                self.refresh_from_db()
                self.measure_mask_in_image(int_result_layer.uid)
            else:
                warnings.warn(
                    f"Mask shape {mask.shape} does not match image shape {image_shape}")
