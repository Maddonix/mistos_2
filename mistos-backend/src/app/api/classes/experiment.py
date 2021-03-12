import warnings
from typing import List, Optional, Set

from app import crud
from app import fileserver_requests as fsr
from app.api import utils_paths, utils_results
from app.api.classes.experiment_group import (DbExperimentGroup,
                                              IntExperimentGroup)
from app.api.classes_com import ComExperiment
from app.api.dependencies import check_sess
from app.api.utils_export import (export_experiment_images,
                                  export_experiment_masks)
from pydantic import BaseModel


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
        sess = check_sess(sess)
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


class IntExperiment(BaseModel):
    '''
    A class to handle calculations and other internal operations with experiments.

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    hint : str, optional
        empty string by default. brief description of the object
    description : str
        empty string by default. Detailed description of the object.
    tags : set
        empty set by default. Keywords to be used in frontend
    experimentGroups : List[app.api.classes_internal.IntExperimentGroup]
        empty list by default. List of all associated experiment groups.

    Methods
    -------
    onInit():
        Initializes object. Object is saved in database and file storage
    to_db_class() -> app.api.classes_db.DbExperiment:
        Returns db class representation
    add_experiment_group(experiment_group_name:str, hint:str="", description:str=""):
        creates new experiment group and saves it to experiment and database.
    calculate_results():
        calls calculate result method of each experiment group
    export_experiment():
        exporter module to handle experiment result export
    '''
    uid: int
    name: str
    hint: str = ""
    description: str = ""
    tags: Set[str] = set()
    experiment_groups: List[IntExperimentGroup] = []

    def on_init(self):
        '''
        Initializes object and saves it to db
        '''
        # should be called on every creation
        if self.uid == -1:
            print("On Init IntExperiment:")
            db_experiment = self.to_db_class()
            db_experiment.create_in_db()
            self.uid = db_experiment.uid

            print(f"New Experiment created with id {self.uid}")

    def to_db_class(self):
        '''
        Returns object's db_class representation.
        '''
        experiment_groups = [experiment_group.to_db_class()
                             for experiment_group in self.experiment_groups]

        kwargs = self.dict()
        kwargs["experiment_groups"] = experiment_groups
        return DbExperiment(**kwargs)

    def add_experiment_group(self, experiment_group_name: str, hint: str = "", description: str = ""):
        '''
        Creates a new experiment group and adds it to the experiment object and in the database.

        Parameters:

            - experiment_group_name(str): name of the new group
            - hint(str): empty string by default. brief description of the group
            - description(str): empty string by default. detailed description of the group
        '''
        experiment_group = IntExperimentGroup(
            uid=-1,
            experiment_id=self.uid,
            name=experiment_group_name,
            hint=hint,
            description=description,
        )
        experiment_group.on_init()
        self.experiment_groups.append(experiment_group)

    def calculate_results(self):
        '''
        This function calls every experiment_group and calculates the corresponding result object.
        '''
        results_groups = []
        assert len(self.experiment_groups) > 0
        for group in self.experiment_groups:
            results_groups.append(group.calculate_result())

    def export_experiment(self, export_types: dict):
        '''
        Function exports the experiment.
        To be done: Exports currently depend on local paths, should be returned as file stream to frontend.

        Parameters:

            export_types(dict): dictionary holding boolean values for all strings (except a list of integers for images_single_channel) of app.api.cfg_classes.export_types. Specifies what exports should be performed.
                images - bool
                masks - bool
                rois - bool, will only be exported in original format
                rescaled - bool
                z_projection - bool
                masks_binary - bool
                masks_png - bool
                images_single_channel - int
                x_dim - int
                y_dim - int
        '''
        self.calculate_results()
        # Export result df, is always exported
        result_df = utils_results.generate_experiment_result_df(
            self.experiment_groups)
        utils_paths.create_experiment_export_folder(self.uid, self.name)
        df_export_name = utils_paths.make_experiment_export_df_name(
            self.uid, self.name)
        result_df.to_excel(df_export_name)
        x_dim = export_types["x_dim"]
        y_dim = export_types["y_dim"]

        for group in self.experiment_groups:
            utils_paths.create_experiment_group_export_folder(
                group.uid, group.name, self.uid, self.name)
            if export_types["images"]:
                utils_paths.create_images_export_folder(
                    group.uid, group.name, self.uid, self.name, False)
            if export_types["masks"]:
                utils_paths.create_masks_export_folder(
                    group.uid, group.name, self.uid, self.name, False)
            if export_types["rois"]:
                utils_paths.create_rois_export_folder(
                    group.uid, group.name, self.uid, self.name, False)
            if export_types["rescaled"]:
                utils_paths.create_images_export_folder(
                    group.uid, group.name, self.uid, self.name, True)
                utils_paths.create_masks_export_folder(
                    group.uid, group.name, self.uid, self.name, True)
            if export_types["images"]:
                for image in group.images:
                    export_experiment_images(
                        self,
                        group,
                        image,
                        export_rescaled=export_types["rescaled"],
                        export_single_channel=export_types["images_single_channel"],
                        export_max_z_project=export_types["z_projection"],
                        x_dim=x_dim,
                        y_dim=y_dim)
            if export_types["masks"]:
                for result_layer_id in group.result_layer_ids:
                    export_experiment_masks(
                        experiment=self,
                        group=group,
                        result_layer_id=result_layer_id,
                        export_binary=export_types["masks_binary"],
                        export_png=export_types["masks_png"],
                        export_rescaled=export_types["rescaled"],
                        export_max_z_project=export_types["z_projection"],
                        export_rois=export_types["rois"],
                        x_dim=x_dim,
                        y_dim=y_dim
                    )
