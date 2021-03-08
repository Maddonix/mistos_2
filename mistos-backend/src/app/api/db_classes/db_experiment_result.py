from app import crud
from app import fileserver_requests as fsr
from app.api.dependencies import check_sess
from app.api.classes_internal import IntExperimentResult
from app.api.classes_com import ComExperimentResult

from pydantic import BaseModel, Optional


class DbExperimentResult(BaseModel):
    '''
    A class to handle database and file storage of ExperimentResults

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str
        brief description of the object
    description : str
        a detailed description of the experiment result
    experiment_group_id : int
        unique identifier of the associated experiment group
    result_type: str
        describes type of result layer. Must be one of strings defined in app.api.cfg_classes.result_types
    path : str, optional
        path to file storage, will be automatically generated when object is saved to database.

    Methods
    -------
    to_int_class()->app.api.classes_internal.IntExperimentResult:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComExperimentResult:
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
    name: str = ""
    hint: str = ""
    description: str = ""
    experiment_group_id: int
    result_type: constr(regex=cfg_classes.result_type_regex)
    path: Optional[str] = ""

    def to_int_class(self):
        '''Returns c_int.IntExperimentResult'''
        kwargs = self.dict()
        kwargs["data"] = fsr.load_result_df(self.path)
        return IntExperimentResult(**kwargs)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Path and id are generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        sql_result = crud.create_experiment_result(self)
        self.uid = sql_result.id
        self.path = sql_result.path

    def to_com_class(self):
        '''Returns c_com.ComExperimentResult'''
        kwargs = self.dict()
        kwargs["experimentGroups"] = [g.uid for g in self.experiment_groups]
        kwargs["resultType"] = self.result_type
        return ComExperimentResult(**kwargs)
