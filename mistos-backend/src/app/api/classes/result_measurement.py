from pathlib import Path
from typing import Any, Optional

from app import crud
from app import fileserver_requests as fsr
from app.api.classes_com import ComResultMeasurement
from app.api.dependencies import check_sess
from pydantic import BaseModel


class DbResultMeasurement(BaseModel):
    '''
    A class to handle database and file storage of ResultMeasurements

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str, optional
        empty string by default. Brief description of the object
    image_id : int
        unique identifier of the associated image
    result_layer_id: int
        unique identifier of the associated result layer
    path : str, optional
        empty string by default. path to file storage. will be automatically generated when object is saved to database.
    path_summary : str, optional
        empty string by default. path to file storage of measurement summary. will be automatically generated when object is saved to database.


    Methods
    -------
    to_int_class()->app.api.classes_internal.IntResultMeasurement:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComResultMeasurement:
        returns object as com_class. 
    create_in_db(sess = None):
        creates object in database, updates objects path and uid attributes accordingly. Uses default session if none is passed.   
    '''
    uid: int
    name: str
    hint: str = ""
    image_id: int
    result_layer_id: int
    path: Optional[Path]
    path_summary: Optional[Path]

    def to_int_class(self):
        '''Returns object as int class. Loads measurement and summary in the process.'''
        kwargs = self.dict()
        kwargs["measurement"] = fsr.load_measurement(self.path)
        kwargs["measurement_summary"] = fsr.load_measurement_summary(
            self.path_summary)
        del kwargs["path"]
        del kwargs["path_summary"]
        return IntResultMeasurement(**kwargs)

    def to_com_class(self):
        '''Returns object as com class.'''
        kwargs = self.dict()
        kwargs["imageId"] = self.image_id
        kwargs["resultLayerId"] = self.result_layer_id
        kwargs["measurement_summary"] = fsr.load_measurement_summary(
            self.path_summary)
        del kwargs["path"]
        del kwargs["path_summary"]

        return ComResultMeasurement(**kwargs)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Path, path_summary and id are generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        sql = crud.create_result_measurement(self, sess)
        self.uid = sql.id
        self.path = Path(sql.path)
        self.path_summary = Path(sql.path_summary)


class IntResultMeasurement(BaseModel):
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
    result_layer_id : int
        unique identifier of the associated result_layer
    measurement : Any
        array with shape (n_labels, n_channel, n_features), features are defined in app.api.utils_results.features.
        calculated by app.api.utils_results.calculate_measurement()
    measurement_summary : Any
        dictionary with summary of the measurement.

    Methods
    -------
    onInit():
        Initializes object. Object is saved in database and file storage
    to_db_class():
        Returns object as DbResultMeasurement object.
    save_measurement(path: pathlib.Path, path_summary: pathlib.Path):
        Saves the attributes "measurement" and "measurement_summary" to given paths.
    '''
    uid: int
    name: str
    hint: str = ""
    image_id: int
    result_layer_id: int
    measurement: Any
    measurement_summary: Any

    def on_init(self):
        '''
        Method to initialize the object. Calls DbResultMeasurement.create_in_db() to save to db. This generates uid and paths to store data
        Then calls the class' save_measurement method to save both.
        '''
        if self.uid == -1:
            db_result_measurement = self.to_db_class()
            db_result_measurement.create_in_db()
            self.uid = db_result_measurement.uid
            self.save_measurement(db_result_measurement.path,
                                  db_result_measurement.path_summary)

    def to_db_class(self):
        '''
        Transforms internal class representation to db class representation.

        To be done: db class has no path after transformation?!
        '''
        kwargs = self.dict()
        del kwargs["measurement"]
        del kwargs["measurement_summary"]
        db_result_measurement = DbResultMeasurement(**kwargs)
        return db_result_measurement

    def save_measurement(self, path: Path, path_summary: Path):
        '''
        Method calls fileserver_requests.save_measurement and fsr.save_measurement_summary to save both attributes to given paths.
        '''
        fsr.save_measurement(self.measurement, path)
        fsr.save_measurement_summary(self.measurement_summary, path_summary)
