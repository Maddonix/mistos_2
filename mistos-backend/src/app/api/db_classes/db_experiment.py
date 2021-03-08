from app import crud
from app import fileserver_requests as fsr
from app.api.dependencies import check_sess
from app.api.classes_internal import IntExperiment
from app.api.classes_com import ComExperiment
from app.api.db_classes.db_experiment_group import DbExperimentGroup

from pydantic import BaseModel
from typing import List, Optional, Set
import warnings


class DbExperiment(BaseModel):
    '''
    A class to handle database and file storage of Experiments

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str
        empty string by default. brief description of the object
    description : str
        empty string by default. brief description of the object    
    tags : Set[str] = []
        set of string keywords to easily categorize objects in frontend.
    experiment_groups: Optional[List[DbExperimentGroup]] = []
        emtpy list by default. List of all associated DbExperimentGroup objects

    Methods
    -------
    to_int_class()->app.api.classes_internal.IntImage:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComImage:
        returns object as com_class. 
    create_in_db(sess = None):
        creates object in database, updates objects path and uid attributes accordingly. Uses default session if none is passed.
    refresh_from_db() -> DbImage
        Fetches image from database and returns DbImage object.
    update_name(new_name: str, sess = None):
        updates objects name in database. Uses default session if none is passed.   
    update_hint(new_hint: str, sess = None):
        updates objects hint in database. Uses default session if none is passed.
    update_description(new_description: str, sess = None):
        updates objects description in database. Uses default session if none is passed.
    update_tags: 
        TO BE DONE
    delete_experiment_group(experiment_group_id: int, sess=None):
        Function deletes an experiment group from storage and this experiment by uid. Uses default session if none is passed.
    delete(sess=None): 
        Function deletes the experiment from the db. Uses default session if none is passed.

    '''
    uid: int
    name: str
    hint: str
    description: str
    tags: Set[str] = set()
    experiment_groups: Optional[List[DbExperimentGroup]] = []

    def to_int_class(self):
        '''Returns IntExperiment object'''
        kwargs = self.dict()
        kwargs["experiment_groups"] = [group.to_int_class()
                                       for group in self.experiment_groups]
        return IntExperiment(**kwargs)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Id is generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        sql_experiment = crud.create_experiment(self, sess)
        self.uid = sql_experiment.id

    def to_com_class(self):
        '''Returns ComExperiment object'''
        kwargs = self.dict()
        kwargs["experimentGroups"] = [group.to_com_class()
                                      for group in self.experiment_groups]
        kwargs["tags"] = list(self.tags)
        return ComExperiment(**kwargs)

    def update_name(self, new_name: str, sess=None):
        '''
        This function expects a new name as string and calls crud.update_experiment_name to update the name.

        Parameters:

            - new_name(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess()
        crud.update_experiment_name(self.uid, new_name, sess)

    def update_hint(self, new_hint: str, sess=None):
        '''
        This function expects a new hint as string and calls crud.update_experiment_hint to update the hint.

        Parameters:

            - new_hint(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_experiment_hint(self.uid, new_hint, sess)

    def update_description(self, new_description: str, sess=None):
        '''
        This function expects a new description as string and calls crud.update_experiment_description to update the description.

        Parameters:

            - new_description(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_experiment_description(self.uid, new_description, sess)

    def update_tags(self, new_tags, sess=None):
        ''' to be done '''
        warnings.warn("Function not yet implemented")

    def delete_experiment_group(self, experiment_group_id: int, sess=None):
        '''
        Function deletes an experiment group by uid.

        Parameters: 

            - experiment_group_id(int): id of the experiment group to be deleted
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.delete_experiment_group_by_id(experiment_group_id, sess)

    def delete(self, sess=None):
        '''
        Function deletes the experiment from the db

        Parameters: 

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.delete_experiment_by_id(self.uid, sess)
