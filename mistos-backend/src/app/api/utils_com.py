import app.api.classes_com as classes_com
import app.crud as crud
from app.api import cfg_classes

# Images
def get_com_image_list():
    '''
    This function fetches all images from the database and returns them as list of ComImage objects.
    '''
    db_image_list = crud.read_all_images()
    com_image_list = [db_image.to_com_class() for db_image in db_image_list]
    return com_image_list

def get_com_image_by_uid(image_uid:int):
    '''
    This function expects the uid of an image, fetches it from the db and returns it as a ComImage object.
    '''
    db_img = crud.read_db_image_by_uid(image_uid)
    com_img = db_img.to_com_class()

    return com_img

# Classifier
def get_com_clf_list(_type):
    '''
    This function fetches all classifiers from the database and returns them as filtered list of ComClassifier objects.
    
    keyword arguments:
    type -- if none, all clf are returned, otherwise string must be valid clf_type ("rf_segmentation", "deepflash_model")
    '''
    db_clf_list = crud.read_all_classifiers()
    if _type:
        assert _type in cfg_classes.classifier_types
        com_classifier_list = [db_clf.to_com_class() for db_clf in db_clf_list if db_clf.clf_type == _type]
    else:
        com_classifier_list = [db_clf.to_com_class() for db_clf in db_clf_list]
    
    return com_classifier_list


def get_com_classifier_by_uid(classifier_uid:int):
    '''
    This function expects the uid of an classifier, fetches it from the db and returns it as a ComClassifier object.
    '''
    db_clf = crud.read_db_classifier_by_uid(classifier_uid)
    com_clf = db_clf.to_com_class()

    return com_clf

# Experiments
def get_com_experiment_list():
    '''
    This function fetches all experiments from the database and returns them as list of ComExperiment objects.
    '''
    db_exp_list = crud.read_all_experiments()
    com_exp_list = [db_exp.to_com_class() for db_exp in db_exp_list]
    return com_exp_list

def get_com_experiment_by_uid(experiment_uid:int):
    '''
    This function expects the uid of an experiment, fetches it from the db and returns it as a ComExperiment object.
    '''
    com_exp = crud.read_experiment_by_uid(experiment_uid).to_com_class()

    return com_exp