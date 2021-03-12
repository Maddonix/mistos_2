from pathlib import Path
from typing import Optional, Any

from app import crud
from app import fileserver_requests as fsr
from app.api.classes_com import ComExperimentResult
from app.api.dependencies import check_sess
from pandas import DataFrame
from pydantic import BaseModel, constr
from app.api import cfg_classes


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
    path : pathlib.Path, optional
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
    path: Optional[Path]

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
        self.path = Path(sql_result.path)

    def to_com_class(self):
        '''Returns c_com.ComExperimentResult'''
        kwargs = self.dict()
        kwargs["experimentGroups"] = [g.uid for g in self.experiment_groups]
        kwargs["resultType"] = self.result_type
        return ComExperimentResult(**kwargs)


class IntExperimentResult(BaseModel):
    '''
    A class to handle calculations and other internal operations with ExperimentResults.

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str, optional
        empty string by default. brief description of the object.
    description : str, optional
        empty string by default. detailed description of the object.
    experiment_group_id : int
        unique identifier of the associated experiment_group
    result_type: str
        describes type of result. Must be one of strings defined in app.api.cfg_classes.result_types
    data : pd.DataFrame, optional
        DataFrame summarizing the result

    Methods
    -------
    onInit():
        Initializes object. Object is saved in database and file storage
    to_db_class():
        Transforms object to db_class
    '''
    uid: int
    name: str = ""
    hint: Optional[str] = ""
    description: Optional[str] = ""
    experiment_group_id: int
    result_type: constr(regex=cfg_classes.result_type_regex)
    data: Any

    def on_init(self):
        # should be called on every creation
        if self.uid == -1:
            db_result = self.to_db_class()
            db_result.create_in_db()
            self.uid = db_result.uid
            fsr.save_result_df(self.data, db_result.path)
            print(f"New Result created with id {self.uid}")

    def to_db_class(self):
        kwargs = self.dict()
        del kwargs["data"]
        return DbExperimentResult(**kwargs)
