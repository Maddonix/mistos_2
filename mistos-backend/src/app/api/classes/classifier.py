from pathlib import Path
from typing import Any, Optional

from app import crud
from app import fileserver_requests as fsr
from app.api import cfg_classes
from app.api.classes.experiment_group import DbExperimentGroup
from app.api.classes_com import ComClassifier
from app.api.dependencies import check_sess
from pydantic import BaseModel, constr


class DbClassifier(BaseModel):
    '''
    A class to handle database and file storage of Classifiers

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    clf_type: str
        describes type of classifier. Must be one of strings defined in app.api.cfg_classes.classifier_types
    path_clf : pathlib.Path, optional
        path to file storage of classifier, will be automatically generated when object is saved to database.
    path_test_train: pathlib.Path, optional
        path to file storage of test_train data, will be automatically generated when object is saved to database (currently just for random forest classifiers).
    params: dict = {}
        currently a not further specified dictionary to store information of parameters the classifier was trained with
    metrics: dict = {}
        currently a not further specified dictionary to store information of the classifiers evaluation metrics
    tags: set = set()
        set of string keywords to easily categorize objects in frontend.

    Methods
    -------
    to_int_class()->app.api.classes_internal.IntClassifier:
        returns object as int_class. Loads layer array from file path in the process.
    to_com_class()->app.api.classes_com.ComClassifier:
        returns object as com_class. 
    create_in_db(sess = None):
        creates object in database, updates objects path and uid attributes accordingly. Uses default session if none is passed.
    delete(sess = None):
        deletes object in database and file storage. Uses default session if none is passed.
    update_name(new_name: str, sess = None):
        updates objects name in database. Uses default session if none is passed.    
    '''
    uid: int
    name: str = ""
    clf_type: constr(regex=cfg_classes.classifier_type_regex)
    path_clf: Optional[Path]
    path_test_train: Optional[Path]
    params: dict = {}
    metrics: dict = {}
    tags: set = set()

    def to_int_class(self):
        '''Returns IntClassifier object'''
        kwargs = self.dict()
        if self.clf_type == "rf_segmentation":
            clf = fsr.load_classifier(self.path_clf)
            test_train_data = fsr.load_classifier_test_train(
                self.path_test_train)
        if self.clf_type == "deepflash_model":
            clf = self.path_clf
            test_train_data = []
        kwargs["test_train_data"] = test_train_data
        kwargs["classifier"] = clf
        del kwargs["path_clf"]
        del kwargs["path_test_train"]
        return IntClassifier(**kwargs)

    def to_com_class(self):
        '''Returns ComClassifier Object'''
        kwargs = self.dict()
        kwargs["tags"] = list(self.tags)
        kwargs["clfType"] = self.clf_type
        return ComClassifier(**kwargs)

    def create_in_db(self, sess=None):
        '''
        Creates object in db. Id is generated and updated in object. 

        Parameters:

            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        sql_classifier = crud.create_classifier(self, sess)
        self.uid = sql_classifier.id
        self.path_clf = Path(sql_classifier.path_clf)
        self.path_test_train = Path(sql_classifier.path_test_train)

    def update_name(self, new_name: str, sess=None):
        '''
        Calls crud.update_result_layer_name to update name.

        Parameters:

            - new_name(str): new name string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.update_classifier_name(self.uid, new_name, sess)

    def delete(self, sess=None):
        '''
        Deletes a classifier from db and file storage

        Parameters:

            - new_name(str): new name string to be saved.
            - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
        '''
        sess = check_sess(sess)
        crud.delete_classifier(self, sess)


class IntClassifier(BaseModel):
    '''
    A class to handle calculations and other internal operations with experiments.

    Attributes
    ----------
    uid : int
        the objects unique identifier
    name : str 
        the objects name
    clf_type : str
        describes type of classifier, must be in app.api.cfg_classes.clf_types
    test_train_data : Any
    params : dict
    metrics : dict
    tags : set
        empty set by default. Keywords to be used in frontend

    Methods
    -------
    onInit():
        Initializes object. Object is saved in database and file storage
    to_db_class() -> app.api.classes_db.DbClassifier:
        Returns db class representation
    is_multichannel():
        helper method for rf segmentation, will be depreceated
    '''
    uid: int
    name: str = ""
    clf_type: constr(regex=cfg_classes.classifier_type_regex)
    classifier: Any
    test_train_data: Any
    params: dict
    metrics: dict
    tags: set = set()

    def on_init(self):
        print("IntClassifier on init")
        print(self.dict())
        db_classifier = self.to_db_class()
        db_classifier.create_in_db()
        self.uid = db_classifier.uid

        path_clf = db_classifier.path_clf
        path_test_train = db_classifier.path_test_train

        if self.clf_type == "rf_segmentation":
            fsr.save_classifier(self.classifier, path_clf)
            fsr.save_classifier_test_train(
                self.test_train_data, path_test_train)

        if self.clf_type == "deepflash_model":
            # We expect self.classifier to be a list of pathlib.Paths
            fsr.save_deepflash_model(self.classifier, path_clf)
        print(f"UID: {self.uid}")

    def to_db_class(self):
        kwargs = self.dict()
        del kwargs["classifier"]
        del kwargs["test_train_data"]
        if not self.uid == -1:
            kwargs["path_clf"] = self.classifier

        return DbClassifier(**kwargs)

    # RF SEGMENTATION METHODS
    def is_multichannel(self):
        if self.clf_type == "rf_segmentation":
            return self.params["multichannel"]
        else:
            print("Multichannel is not an option for clf of type df_segmentation")
            return False
