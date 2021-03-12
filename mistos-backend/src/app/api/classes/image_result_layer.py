from app import fileserver_requests as fsr
import numpy as np
from pydantic import BaseModel, constr
from typing import Optional, Any
from app import crud
from app.api.dependencies import check_sess
from app.api.classes_com import ComImageResultLayer
from app.api import utils_import
from pathlib import Path
from app.api import cfg_classes


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
    path : pathlib.Path, optional
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
    path: Optional[Path]

    def to_int_class(self):
        ''' Returns object as com class'''
        kwargs = self.dict()
        data = fsr.load_zarr(self.path)
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
        self.path = Path(sql.path)

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


class IntImageResultLayer(BaseModel):
    '''
    A class to handle calculations and other internal operations with result layers.

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str, optional
        empty string by default. brief description of the object
    image_id : int
        unique identifier of the associated image
    layer_type: str
        describes type of result layer. Must be one of strings defined in app.api.cfg_classes.layer_types
    data : Any

    Methods
    -------
    onInit():
        Initializes object. Object is saved in database and file storage
    delete():
        Removes a result_layer as well as the associated measurements
    to_db_class():
        Transforms object to db_class
    '''
    uid: int
    name: str
    hint: Optional[str] = ""
    image_id: int
    layer_type: constr(regex=cfg_classes.layer_type_regex)
    data: Any

    def on_init(self):
        '''
        Method to initialize the object. Asserts that result layer has 3 dimensions, then calls DbImageResultLayer.create_in_db() to save to db. This generates uid and path to store data
        Then calls stores label layer to file storage as zarr.
        '''
        if self.uid == -1:
            if len(self.data.shape) == 2:
                print(
                    f"WARNING: Result Layer was initialized with shape {self.data.shape}, appending new axis to match universal layer shape (z,y,x)")
                self.data = self.data[np.newaxis, ...]
            assert len(self.data.shape) == 3
            db_layer = self.to_db_class()
            db_layer.create_in_db()
            self.uid = db_layer.uid
            self.data = self.data.astype(int)
            print(f"New Layer created with id {self.uid}")
            fsr.save_zarr(
                path=db_layer.path,
                array=self.data
            )

    def delete(self):
        '''
        This function removes a result_layer as well as the associated measurements
        '''
        db_layer = self.to_db_class()
        db_layer.delete()

    def to_db_class(self):
        '''
        Transforms internal class representation to db class representation.

        To be done: db class has no path after transformation?!
        '''

        args = self.dict()
        del args["data"]
        db_image_result_layer = DbImageResultLayer(**args)

        return db_image_result_layer
