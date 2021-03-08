from app import crud
from app import fileserver_requests as fsr
from app.api.dependencies import check_sess
from app.api.classes_internal import IntImage
from app.api.classes_com import ComImage
from app.api.db_classes.db_image_result_layer import DbImageResultLayer
from app.api.db_classes.db_result_measurement import DbResultMeasurement
from app.api import utils_import

from pydantic import BaseModel
from typing import List, Optional, Set


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
    path_metadata: str, optional
        path to the images metadata ".json". Automatically generated as image is saved to database.
    path_image: str, optional
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
    path_metadata: Optional[str]
    path_image: Optional[str]
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
            data, metadata = utils_import.load_zarr(
                kwargs["path_image"], kwargs["path_metadata"])
            kwargs["data"] = data
        else:
            metadata = fsr.load_metadata(self.path_metadata)
            kwargs["data"] = None
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
        self.path_image = sql_image.path_image
        self.path_metadata = sql_image.path_metadata

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
        metadata = fsr.load_metadata(self.path_metadata)
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
