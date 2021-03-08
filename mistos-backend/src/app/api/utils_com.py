import app.api.classes_com as classes_com
import app.crud as crud
from app.api import cfg_classes
from app.api.dependencies import check_sess

# Images


def get_com_image_list(sess=None):
    '''
    This function fetches all images from the database and returns them as list of ComImage objects.

    Parameters:

        - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
    '''
    sess = check_sess(sess)
    db_image_list = crud.read_all_images(sess)
    com_image_list = [db_image.to_com_class() for db_image in db_image_list]
    return com_image_list


def get_com_image_by_uid(image_uid: int, sess=None):
    '''
    This function expects the uid of an image, fetches it from the db and returns it as a ComImage object.

    Parameters:

        - image_uid(int): uid of image to fetch.
        - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
    '''
    sess = check_sess(sess)
    db_img = crud.read_db_image_by_uid(image_uid, sess)
    com_img = db_img.to_com_class()
    return com_img

# Classifier


def get_com_clf_list(clf_type: str, sess=None):
    '''
    This function fetches all classifiers from the database and returns them as filtered list of ComClassifier objects.

    Parameters:

        - clf_type(str): str which matches element of app.api.cfg_classes.clf_types to filter classifier list by. 
        - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
    '''
    sess = check_sess(sess)
    db_clf_list = crud.read_all_classifiers(sess)
    if clf_type:
        assert clf_type in cfg_classes.classifier_types
        com_classifier_list = [db_clf.to_com_class()
                               for db_clf in db_clf_list if db_clf.clf_type == clf_type]
    else:
        com_classifier_list = [db_clf.to_com_class() for db_clf in db_clf_list]
    return com_classifier_list


def get_com_classifier_by_uid(classifier_uid: int, sess=None):
    '''
    This function expects the uid of an classifier, fetches it from the db and returns it as a ComClassifier object.

    Parameters:

        - classifier_uid(int): uid of classifier to fetch.
        - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
    '''
    sess = check_sess(sess)
    db_clf = crud.read_db_classifier_by_uid(classifier_uid)
    com_clf = db_clf.to_com_class()
    return com_clf

# Experiments


def get_com_experiment_list(sess=None):
    '''
    This function fetches all experiments from the database and returns them as list of ComExperiment objects.

    Parameters:

        - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
    '''
    sess = check_sess(sess)
    db_exp_list = crud.read_all_experiments(sess)
    com_exp_list = [db_exp.to_com_class() for db_exp in db_exp_list]
    return com_exp_list


def get_com_experiment_by_uid(experiment_uid: int, sess=None):
    '''
    This function expects the uid of an experiment, fetches it from the db and returns it as a ComExperiment object.

    Parameters:

        - experiment_uid(int): uid of experiment to fetch.
        - sess(sqlalchemy.orm.Session): The database session to be used, if no session is passed default session will be used (app.api.dependencies.get_db).
    '''
    sess = check_sess(sess)
    com_exp = crud.read_experiment_by_uid(experiment_uid, sess).to_com_class()
    return com_exp
