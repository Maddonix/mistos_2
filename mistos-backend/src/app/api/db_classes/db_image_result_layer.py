from app import crud
from app import fileserver_requests as fsr
from app.api.dependencies import check_sess
from app.api.classes_internal import IntImageResultLayer
from app.api.classes_com import ComImageResultLayer
from app.api import utils_import
from app.api import cfg_classes

from pydantic import BaseModel, constr
from typing import Optional


class DbImageResultLayer(BaseModel):
    '''
    A class to handle database and file storage of ImageResultLayers

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str
        brief description of the object
    image_id : int
        unique identifier of the associated image
    layer_type: str
        describes type of result layer. Must be one of strings defined in app.api.cfg_classes.layer_types
    path : str, optional
        path to file storage, will be automatically generated when object is saved to database.

    Methods
    -------
    to_int_class()->app.api.classes_internal.IntImageResultLayer:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComImageResultLayer:
        returns object as com_class. 
    create_in_db(sess = None):
        creates object in database, updates objects path and uid attributes accordingly. Uses default session if none is passed.
    delete(sess = None):
        deletes object in database and file storage. Uses default session if none is passed.
    update_hint(new_hint: str, sess = None):
        updates objects hint in database. Uses default session if none is passed.
    update_name(new_name: str, sess = None):
        updates objects name in database. Uses default session if none is passed.    
    '''
    uid: int
    name: str
    hint: str
    image_id: int
    layer_type: constr(regex=cfg_classes.layer_type_regex)
    path: Optional[str]

    def to_int_class(self):
        ''' Returns object as com class'''
        kwargs = self.dict()
        data = utils_import.load_label_layer_from_zarr(self.path)
        kwargs["data"] = data
        del kwargs["path"]
        return IntImageResultLayer(**kwargs)

    def to_com_class(self):
        ''' Returns object as com class'''
        kwargs = self.dict()
        kwargs["imageId"] = self.image_id
        kwargs["layerType"] = self.layer_type
        return ComImageResultLayer(**kwargs)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Path and id are generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        sql = crud.create_result_layer(self, sess)
        self.uid = sql.id
        self.path = sql.path

    def delete(self, sess=None):
        '''
        Calls crud method to Delete all associated measurements and the layer itself.
        '''
        sess = check_sess(sess)
        crud.delete_result_layer(self, sess)

    def update_hint(self, new_hint: str, sess=None):
        '''
        Calls crud.update_result_layer_hint to save string as new hint.

        Parameters:

            - new_hint(str): new hint string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.update_result_layer_hint(self.uid, new_hint, sess)

    def update_name(self, new_name: str, sess=None):
        '''
        Calls crud.update_result_layer_name to update name.

        Parameters:

            - new_name(str): new name string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.update_result_layer_name(self.uid, new_name, sess)
