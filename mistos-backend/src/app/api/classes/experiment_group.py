from typing import List

from app import crud
from app import fileserver_requests as fsr
from app.api import utils_results
from app.api.classes.experiment_result import IntExperimentResult
from app.api.classes.image import DbImage, IntImage
from app.api.classes_com import ComExperimentGroup
from app.api.dependencies import check_sess
from pydantic import BaseModel, constr
import app.crud as crud  # import read_measurement_by_result_layer_uid, read_image_by_uid


class DbExperimentGroup(BaseModel):
    '''
    A class to handle database and file storage of Experiment Groups.

    Attributes
    ----------
    uid : int
        the objects unique identifier.
    name : str 
        the objects name.
    hint : str = ""
        empty string by default. brief description of the object.
    description : str = ""
        empty string by default. detailed description of the object.
    experiment_id : int
        uid of associated experiment.
    images : List[DbImage] = []
        List of the experiment groups images as db_class
    result_layer_ids: List[int] = []
        emtpy list by default. List of all associated DbImageResultLayer objects' ids.
    measurement_ids: List[int] = []
        To be depreceated
        emtpy list by default. List of all associated DbResultMeasurement objects' ids.

    Methods
    -------
    to_int_class()->app.api.classes_internal.IntExperimentGroup:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComExperimetnGroup:
        returns object as com_class. 
    create_in_db(sess = None):
        creates object in database, updates objects path and uid attributes accordingly. Uses default session if none is passed.
    add_image_by_uid(image_uid: int, sess = None)
        adds image to experiment group. Uses default session if none is passed.
    remove_image_by_uid(image_uid: int, sess = None)
        removes image from experiment group. Uses default session if none is passed.
    add_result_layer_uid(result_layer_uid: int, sess = None)
        adds result layer to group by uid. Uses default session if none is passed.
    add_measurement(measurement_uid: int, sess = None):
        Adds measurement with given measurement_uid to group. Uses default session if none is passed.
    delete(sess = None):
        deletes object in database and file storage. Uses default session if none is passed.
    update_name(new_name: str, sess = None):
        updates objects name in database. Uses default session if none is passed.   
    update_hint(new_hint: str, sess = None):
        updates objects hint in database. Uses default session if none is passed.
    update_description(new_description: str, sess = None):
        updates objects description in database. Uses default session if none is passed.
    update_images(image_id_list: List[int], sess = None):
        This function expects a list of image ids and calls crud.update_experiment_group_images to update the associated images. Uses default session if none is passed.
    remove_image(image_uid: int, sess = None):
        Function expects an image id. Removes image from the group. Also removes result layer of this image from the group. Uses default session if none is passed.
    remove_measurement(measurement_uid: int, sess = None):
        Function expects an result_layer_uid. Removes result_layer from the group. Uses default session if none is passed.
    remove_measurement(measurement_uid: int, sess = None):
        Function expects an measurement_uid. Removes measurement from the group. Uses default session if none is passed.
    refresh_from_db(sess = None) -> DbExperimentGroup: 
        Fetches expperiment group from and returns it as DbExperimentGroup object. Does not update the object itself. Uses default session if none is passed.
    '''
    uid: int
    name: str
    hint: str = ""
    description: str = ""
    experiment_id: int
    images: List[DbImage] = []
    result_layer_ids: List[int] = []
    measurement_ids: List[int] = []

    def to_int_class(self):
        '''Returns IntExperimentGroup object'''
        kwargs = self.dict()
        images = [img.to_int_class() for img in self.images]
        kwargs["images"] = images
        int_experiment_group = IntExperimentGroup(**kwargs)
        return int_experiment_group

    def to_com_class(self):
        '''Returns ComExperimentGroup object'''
        kwargs = self.dict()
        kwargs["experimentId"] = self.experiment_id
        kwargs["images"] = [i.to_com_class() for i in self.images]
        kwargs["resultLayerIds"] = self.result_layer_ids
        kwargs["measurementIds"] = self.measurement_ids

        return ComExperimentGroup(**kwargs)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Id is generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        sql_group = crud.create_experiment_group(self, sess)
        self.uid = sql_group.id

    def add_image_by_uid(self, image_uid: int, sess=None):
        '''
        Adds image with given image_uid to group.

        Parameters:

            - image_uid(int): uid of image to be added to group.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        db_image = crud.add_image_to_experiment_group(self, image_uid)
        return db_image.to_int_class()

    def remove_image_by_uid(self, image_uid: int, sess=None):
        '''
        Removes image with given image_uid from group.

        Parameters:

            - image_uid(int): uid of image to be added to group.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.remove_image_from_experiment_group(self, image_uid, sess)

    def add_result_layer(self, result_layer_uid: int, sess=None):
        '''
        This function expects a layer uid.
        It retrieves the group's layer list and checks if another layer with of the same image is present in this experiment group. 
        If so, the other layer is removed first, then the current layer is added.

        Parameters:

            - result_layer_uid(int): uid of result layer to be added to group.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        new_db_result_layer = crud.read_result_layer_by_uid(
            result_layer_uid, sess)
        image_id = new_db_result_layer.image_id
        for current_result_layer_id in self.result_layer_ids:
            current_layer = crud.read_result_layer_by_uid(
                current_result_layer_id)
            if current_layer.image_id == image_id:
                self.remove_result_layer(current_result_layer_id, sess)

        crud.add_result_layer_to_experiment_group(
            self, result_layer_uid, sess)

    def add_measurement(self, measurement_uid: int, sess=None):
        '''
        Adds measurement with given measurement_uid to group.

        Parameters:

            - measurement_uid(int): uid of measurement to be added to group.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.add_measurement_to_experiment_group(self, measurement_uid, sess)

    def update_name(self, new_name: str, sess=None):
        '''
        This function expects a new name as string and calls crud.update_experiment_group_name to update the name.

        Parameters:

            - new_name(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_experiment_group_name(self.uid, new_name)

    def update_hint(self, new_hint: str, sess=None):
        '''
        This function expects a new hint as string and calls crud.update_experiment_group_hint to update the hint.

        Parameters:

            - new_hint(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_experiment_group_hint(self.uid, new_hint, sess)

    def update_description(self, new_description: str, sess=None):
        '''
        This function expects a new description as string and calls crud.update_experiment_group_description to update the description.

        Parameters:

            - new_description(str): string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_experiment_group_description(self.uid, new_description)

    def update_images(self, image_id_list: List[int], sess=None):
        '''
        This function expects a list of image ids and calls crud.update_experiment_group_images to update the associated images.

        Parameters:

            - image_id_list(List[int]): list of image ids to be saved as associated images.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.update_experiment_group_images(self.uid, image_id_list, sess)

    def remove_image(self, image_uid: int, sess=None):
        '''
        Function expects an image id. Removes image from the group. Also removes result layer of this image from the group.

        Parameters:

            - image_uid(int): image id to be removed from group
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.remove_image_from_experiment_group(self, image_uid, sess)

        for current_result_layer_id in self.result_layer_ids:
            current_layer = crud.read_result_layer_by_uid(
                current_result_layer_id, sess)
            if current_layer.image_id == image_uid:
                self.remove_result_layer(current_result_layer_id, sess)

    def remove_result_layer(self, result_layer_uid: int, sess=None):
        '''
        Function expects an result_layer_uid. Removes result_layer from the group.

        Parameters:

            - result_layer_uid(int): result_layer_uid to be removed from group
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.remove_result_layer_from_experiment_group(
            self, result_layer_uid, sess=None)

    def remove_measurement(self, measurement_uid: int, sess=None):
        '''
        Function expects an measurement_uid. Removes measurement from the group

        Parameters:

            - measurement_uid(int): measurement_uid to be removed from group
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        crud.remove_measurement_from_experiment_group(
            self, measurement_uid, sess)

    def refresh_from_db(self, sess=None):
        ''' 
        Fetches expperiment group from and returns it as DbExperimentGroup object. Does not update the object itself.

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db)
        '''
        sess = check_sess(sess)
        updated_info = crud.read_experiment_group_by_uid(
            self.uid, sess)
        return updated_info


class IntExperimentGroup(BaseModel):
    '''
    A class to handle calculations and other internal operations with experiment groups.

    Attributes
    ----------
    uid : int
        the objects unique identifier
    experiment_id : int
        the corresponding experiment's unique identifier
    name : str 
        the objects name
    hint : str
        empty string by default. Brief description of the experiment group.
    description : str
        empty string by default. Detailed description of the experiment group.
    images : List[app.api.classes_internal.IntImage]
        empty list by default. List of this groups images
    result_layer_ids : List[int]
        empty list by defalut. List of this groups result layers' ids.
    measurement_ids : List[int]
        empty list by defalut. List of this groups measurements' ids.

    Methods
    -------
    on_init():
        Initializes object. Object is saved in database.
    get_experiment_result() -> app.api.classes_internal.IntExperimentResult:
        Returns corresponding IntExperimentResult.
    calculate_result() -> pd.DataFrame:
        Formats measurements of all result layers of this group to one dataframe.
    refresh_from_db():
        Fetches object from database and updates all attributes.
    to_db_class() -> app.api.classes_db.DbExperimentResult:
        Helper method to return object as DbExperimentGroup
    add_image_by_uid(image_uid:int):
        Method to add an image to the experiment_group.
    add_result_layer(uid:int):
        Method to add an result_layer to the experiment_group.
    add_measurement(uid:int):
        Method to add an measurement to the experiment_group.
    remove_image(uid:int):
        Method to remove an image from the experiment_group.
    remove_result_layer(uid:int):
        Method to remove an result_layer from the experiment_group.
    remove_measurement(uid:int):
        Method to remove an measurement from the experiment_group.
    '''
    uid: int
    experiment_id: int
    name: str
    hint: str = ""
    description: str = ""
    images: List[IntImage] = []
    result_layer_ids: List[int] = []
    measurement_ids: List[int] = []

    def on_init(self):
        '''
        Method to initialize the object and save it to the database. Generates id.
        '''
        if self.uid == -1:
            print("On Init IntExperimentGroup:")
            db_group = self.to_db_class()
            db_group.create_in_db()
            self.uid = db_group.uid

            print(f"New Group created with id {self.uid}")

    def get_experiment_result(self) -> IntExperimentResult:
        '''
        Fetches experiment result from db. If not available, calculates it first using self.calculate_result.
        Returns app.api.classes_internal.IntExperimentResult
        '''
        try:
            db_result = crud.read_result_of_experiment_group_by_id(self.uid)
        except:
            self.calculate_result()
            db_result = crud.read_result_of_experiment_group_by_id(self.uid)

        return db_result.to_int_class()

    def calculate_result(self):
        '''
        This function calculates a result from all associated result layers. 
        Calls utils_results.calculate_measurement_df_for_result() to get colnames
        Returns result dataframe.
        '''
        # Read one measurement per image and retrieve measurement np_array in shape (n_label, n_channel, n_features)
        assert len(self.result_layer_ids) > 0
        results = []
        for result_layer_id in self.result_layer_ids:
            # Read Measurement
            c_int_measurement = crud.read_measurement_by_result_layer_uid(
                result_layer_id).to_int_class()
            measurement = c_int_measurement.measurement
            # Read Image
            image_id = c_int_measurement.image_id
            int_image = crud.read_image_by_uid(image_id)

            measurement_df = utils_results.calculate_measurement_df_for_result(
                self.uid, self.name, c_int_measurement, int_image
            )
            results.append(measurement_df)
        result_df = results[0]
        if len(results) > 1:
            for result in results[1:]:
                # merge(result.iloc[1:, :], how = "outer") #dont select index row
                result_df = result_df.append(result, ignore_index=True)
        try:
            db_experiment_result = crud.read_result_of_experiment_group_by_id(
                self.uid)
            print(
                f"Experiment group with id {self.uid} already has a result. Deleting previous result.")
            crud.delete_experiment_result(db_experiment_result.uid)
        except:
            print(
                f"No Result found for experiment group with id {self.uid}, creating new")
        c_int_experiment_result = IntExperimentResult(
            uid=-1,
            name=f"{self.name}_result",
            hint="",
            description="",
            experiment_group_id=self.uid,
            result_type="measure",
            data=result_df
        )
        c_int_experiment_result.on_init()
        self.refresh_from_db()
        return result_df

    def refresh_from_db(self):
        '''
        Method to update object from database.
        '''
        db_image = self.to_db_class()
        updated_info = db_image.refresh_from_db()

        self.name = updated_info.name
        self.hint = updated_info.hint
        self.description = updated_info.description
        self.images = updated_info.images
        self.result_layer_ids = updated_info.result_layer_ids
        self.measurement_ids = updated_info.measurement_ids

    def to_db_class(self):
        '''
        Helper method to return object as DbExperimentGroup
        '''
        _images = [image.to_db_class() for image in self.images]
        kwargs = self.dict()
        kwargs["images"] = _images
        return DbExperimentGroup(**kwargs)

    def add_image_by_uid(self, image_uid: int):
        '''
        Method to add an image to the experiment_group.

        Parameters:

            - image_uid(int): unique identifier of object to add.
        '''
        db_experiment_group = self.to_db_class()
        int_image = db_experiment_group.add_image_by_uid(image_uid)
        # self.images.append(int_image)
        self.refresh_from_db()

    def add_result_layer(self, uid: int):
        '''
        Method to add an result_layer to the experiment_group.

        Parameters:

            - uid(int): unique identifier of object to add.
        '''
        db_experiment_group = self.to_db_class()
        db_experiment_group.add_result_layer(uid)
        self.refresh_from_db()

    def add_measurement(self, uid: int):
        '''
        Method to add an measurement to the experiment_group.

        Parameters:

            - uid(int): unique identifier of object to add.
        '''
        db_experiment_group = self.to_db_class()
        db_experiment_group.add_measurement(uid)
        self.refresh_from_db()

    def remove_image(self, uid: int):
        '''
        Method to remove an image from the experiment_group.

        Parameters:

            - uid(int): unique identifier of object to remove.
        '''
        db_experiment_group = self.to_db_class()
        db_experiment_group.remove_image(uid)
        self.refresh_from_db()

    def remove_result_layer(self, uid: int):
        '''
        Method to remove an result_layer from the experiment_group.

        Parameters:

            - uid(int): unique identifier of object to remove.
        '''
        db_experiment_group = self.to_db_class()
        db_experiment_group.remove_result_layer(uid)
        self.refresh_from_db()

    def remove_measurement(self, uid: int):
        '''
        Method to remove an measurement from the experiment_group.

        Parameters:

            - uid(int): unique identifier of object to remove.
        '''
        db_experiment_group = self.to_db_class()
        db_experiment_group.remove_measurement(uid)
        self.refresh_from_db()
