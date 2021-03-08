from app import crud
from app import fileserver_requests as fsr
from pydantic import BaseModel
from app.api.dependencies import check_sess
from app.api.classes_internal import IntResultMeasurement
from app.api.classes_com import ComResultMeasurement


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
    path: str = ""
    path_summary: str = ""

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
        self.path = sql.path
        self.path_summary = sql.path_summary
