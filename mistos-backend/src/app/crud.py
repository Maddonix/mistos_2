# pylint:disable=not-context-manager
from app.database import engine
from . import db_models
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.api.dependencies import check_sess
from typing import List
import warnings

import app.api.utils_paths as utils_paths
import app.api.utils_db as utils_db
import app.fileserver_requests as fsr

# Utils


# Create


def create_image(image, sess: Session = None):
    '''
    Creates new image entry inside the image-table. Returns sql image object with id and path added.

    Parameters:

        - image(app.api.classes_db.DbImage): The image object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    # if expire_on_commit == False, we can access objects after a session is closes
    # objects will not be in sync with db
    sql_image = db_models.Image(
        name=image.name,
        series_index=image.series_index,
        hint=image.hint,
        tags=image.tags,
        has_bg_layer=image.has_bg_layer,
        bg_layer_id=image.bg_layer_id
    )
    sess.add(sql_image)
    sess.commit()
    sess.refresh(sql_image)
    sql_image.path_image = utils_paths.fileserver.joinpath(
        utils_paths.make_image_path(sql_image.id)).as_posix()
    sql_image.path_metadata = utils_paths.fileserver.joinpath(
        utils_paths.make_metadata_path(sql_image.id)).as_posix()
    sess.commit()
    return sql_image


def create_result_layer(result_layer, sess: Session = None):
    '''
    Creates new result layer entry inside the result-layer-table. Returns sql result layer object with id and path added.

    Parameters:

        - result_layer(app.api.classes_db.DbImageResultLayer): The result layer object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_layer = db_models.ResultLayer(
        name=result_layer.name,
        hint=result_layer.hint,
        layer_type=result_layer.layer_type,
        image_id=result_layer.image_id
    )
    sess.add(sql_layer)
    sess.commit()
    sql_layer.path = utils_paths.fileserver.joinpath(
        utils_paths.make_result_layer_path(sql_layer.id)).as_posix()
    sess.commit()
    sess.refresh(sql_layer)
    return sql_layer


def create_experiment_group(experiment_group, sess: Session = None):
    '''
    Creates new experiment group entry inside the experiment group-table. Returns sql experiment group object with id and path added.

    Parameters:

        - experiment_group(app.api.classes_db.DbExperimentGroup): The experiment group object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    experiment = sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == experiment_group.experiment_id).one()

    sql_group = db_models.ExperimentGroup(
        name=experiment_group.name,
        hint=experiment_group.hint,
        description=experiment_group.description,
        experiment=experiment
    )
    sess.add(sql_group)
    sess.commit()
    return sql_group


def create_experiment_result(experiment_result, sess: Session = None):
    '''
    Creates new experiment result entry inside the experiment result-layer-table. Returns sql experiment result object with id added.

    Parameters:

        - experiment_result(app.api.classes_db.DbExperimentResult): The experiment result object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_result.experiment_group_id).one()

    sql_result = db_models.ExperimentResult(
        name=experiment_result.name,
        hint=experiment_result.hint,
        description=experiment_result.description,
        result_type=experiment_result.result_type,
        experiment_group=sql_experiment_group
    )
    sess.add(sql_result)
    sess.commit()
    sess.refresh(sql_result)
    sql_result.path = utils_paths.fileserver.joinpath(
        utils_paths.make_result_path(sql_result.id)).as_posix()
    sess.commit()
    sess.refresh(sql_result)
    return sql_result


def create_experiment(experiment, sess: Session = None):
    '''
    Creates new experiment entry inside the experiment-table. Returns sql experiment  object with id added.

    Parameters:

        - experiment(app.api.classes_db.DbExperiment): The experiment object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment = db_models.Experiment(
        name=experiment.name,
        hint=experiment.hint,
        description=experiment.description,
        tags=experiment.tags
    )
    sess.add(sql_experiment)
    sess.commit()
    return sql_experiment


def create_result_measurement(result_measurement, sess: Session = None):
    '''
    Creates new result_measurement entry inside the result_measurement-table. Returns sql result_measurement object with id added.

    Parameters:

        - experiment(app.api.classes_db.DbResultMeasurement): The result_measurement object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == result_measurement.image_id).one()
    sql_result_layer = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == result_measurement.result_layer_id).one()

    sql_measurement = db_models.Measurement(
        name=result_measurement.name,
        hint=result_measurement.hint
    )

    sql_image.measurements.append(sql_measurement)
    sql_result_layer.measurements.append(sql_measurement)

    sess.add(sql_measurement)
    sess.commit()
    sess.refresh(sql_measurement)
    sql_measurement.path = utils_paths.fileserver.joinpath(
        utils_paths.make_measurement_path(sql_measurement.id)).as_posix()
    sql_measurement.path_summary = utils_paths.fileserver.joinpath(
        utils_paths.make_measurement_summary_path(sql_measurement.id)).as_posix()
    sess.commit()
    return sql_measurement


def create_classifier(classifier, sess: Session = None):
    '''
    Creates new classifier entry inside the classifier-table. Returns sql classifier object with id added.

    Parameters:

        - classifier(app.api.classes_db.DbClassifier): The classifier object to be added to the database.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_clf = db_models.Classifier(
        name=classifier.name,
        clf_type=classifier.clf_type,
        params=classifier.params,
        metrics=classifier.metrics,
        tags=classifier.tags
    )

    sess.add(sql_clf)
    sess.commit()
    sess.refresh(sql_clf)

    if classifier.clf_type == "rf_segmentation":
        sql_clf.path_clf = utils_paths.fileserver.joinpath(
            utils_paths.make_clf_path(sql_clf.id)).as_posix()
        sql_clf.path_test_train = utils_paths.fileserver.joinpath(
            utils_paths.make_clf_test_train_path(sql_clf.id)).as_posix()
    elif classifier.clf_type == "deepflash_model":
        sql_clf.path_clf = utils_paths.fileserver.joinpath(
            utils_paths.make_deepflash_model_path(sql_clf.id)).as_posix()
        sql_clf.path_test_train = ""
    sess.commit()
    return sql_clf

# Read
# Images


def read_image_by_uid(uid: int, sess: Session = None, for_refresh=False):
    '''
    Expects image uid and returns IntImage object.

    Parameters: 

        - uid(int): Valid Image ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
        - for_refresh(bool): The argument is passed to app.api.classes_db.DbImage.to_int_class.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == uid).one()
    db_image = utils_db.image_sql_to_db(sql_image)
    c_int_image = db_image.to_int_class(for_refresh)
    return c_int_image


def read_db_image_by_uid(uid: int, sess: Session = None):
    '''
    Expects image uid and returns DbImage object.

    Parameters: 

        - uid(int): Valid Image ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == uid).one()
    db_image = utils_db.image_sql_to_db(sql_image)
    return db_image


def read_all_images(sess: Session = None):
    '''
    Fetches all images from db and returns them as list of DbImage objects.

    Parameters: 

        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image_list = sess.query(db_models.Image)
    db_image_list = [utils_db.image_sql_to_db(
        sql_image) for sql_image in sql_image_list]
    return db_image_list


# Classifier


def read_all_classifiers(sess: Session = None):
    '''
    Fetches all classifiers from the database and returns them as list of DbClassifier objects.

    Parameters: 

        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_clf_list = sess.query(db_models.Classifier)
    db_clf_list = [utils_db.classifier_sql_to_db(
        sql_clf) for sql_clf in sql_clf_list]
    return db_clf_list


def read_db_classifier_by_uid(uid: int, sess: Session = None):
    '''
    Expects classifier uid and returns c_db.DbClassifier object.

    Parameters: 

        - uid(int): uid of the classifier to fetch.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_clf = sess.query(db_models.Classifier).filter(
        db_models.Classifier.id == uid).one()
    sql_clf = utils_db.classifier_sql_to_db(sql_clf)
    return sql_clf


# Experiments


def read_all_experiments(sess: Session = None):
    '''
    This function fetches all experiments from the db and returns them as list of DbExperiment objects.

    Parameters: 

        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_exp_list = sess.query(db_models.Experiment)
    db_exp_list = [utils_db.experiment_sql_to_db(
        sql_exp) for sql_exp in sql_exp_list]
    return db_exp_list


def read_experiment_by_uid(uid: int, sess: Session = None):
    '''
    Expects experiment uid and returns c_db.DbExperiment object.

    Parameters: 

        - uid(int): Valid experiment uid.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment = sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == uid).one()
    db_experiment = utils_db.experiment_sql_to_db(sql_experiment)
    return db_experiment


# ExperimentGroup


def read_experiment_group_by_uid(uid: int, sess: Session = None, for_refresh=False):
    '''
    Expects experiment_group uid and returns a c_int.IntExperimentGroup object.

    Parameters: 

        - uid(int): Valid experiment ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
        - for_refresh(bool): The argument is passed to app.api.classes_db.DbExperimentGroup.to_int_class.
    '''
    sess = check_sess(sess)
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    db_experiment_group = utils_db.experiment_group_sql_to_db(
        sql_experiment_group)
    c_int_experiment_group = db_experiment_group.to_int_class()
    return c_int_experiment_group


def read_experiment_db_group_by_uid(uid: int, sess: Session = None):
    '''
    Expects experiment_group uid and returns c_db.DbExperimentGroup object.

    Parameters: 

        - uid(int): Valid experiment ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    db_experiment_group = utils_db.experiment_group_sql_to_db(
        sql_experiment_group)
    return db_experiment_group


def read_result_of_experiment_group_by_id(uid: int, sess: Session = None):
    '''
    Expects uid of experiment group, returns the groups' result as c_db.DbExperimentResultObject

    Parameters: 

        - uid(int): Valid experiment group ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    return utils_db.experiment_result_sql_to_db(sql_group.experiment_result)


def read_result_layers_of_image_uid(uid: int, sess: Session = None):
    '''
    Expects image uid and returns a list of c_db.DbResultLayer objects.

    Parameters: 

        - uid(int): Valid image ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == uid).one()
    sql_result_layers = sql_image.result_layers
    db_result_layers = [utils_db.result_layer_sql_to_db(
        sql_result_layer) for sql_result_layer in sql_result_layers]
    return db_result_layers


def read_result_layer_by_uid(uid: int, sess: Session = None):
    '''
    Expects result layer uid and returns a list of c_db.DbResultLayer objects.

    Parameters: 

        - uid(int): Valid result layer ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_layer = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == uid).one()
    return utils_db.result_layer_sql_to_db(sql_layer)


def read_measurement_by_result_layer_uid(uid: int, sess: Session = None):
    '''
    Expects a result layer uid and returns the correspoinding db_measurement object.

    Parameters: 

        - uid(int): Valid result layer ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_measurement = sess.query(db_models.Measurement).filter(
        db_models.Measurement.result_layer_id == uid).one()
    db_measurement = utils_db.measurement_sql_to_db(sql_measurement)
    return db_measurement


def read_classifier_by_uid(uid: int, sess: Session = None):
    '''
    Expects classifier uid and returns c_int.IntClassifier object.

    Parameters: 

        - uid(int): Valid classifier ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    with SessionLocal(expire_on_commit=False) as sess:
        sql_classifier = sess.query(db_models.Classifier).filter(
            db_models.Classifier.id == uid).one()
        db_classifier = utils_db.classifier_sql_to_db(sql_classifier)
        c_int_classifier = db_classifier.to_int_class()
        return c_int_classifier


def read_classifier_dict_by_type(clf_type: str, sess: Session = None):
    '''
    Expects clf_type as string as defined in utils_db and returns a dict of {name: id}.

    Parameters: 

        - clf_type(str): Valid classifier type, for available types see app.api.cfg_classes.classifier_types.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_classifiers = sess.query(db_models.Classifier).filter(
        db_models.Classifier.clf_type == clf_type)
    clf_dict = {}
    for sql_classifier in sql_classifiers:
        clf_dict[f"{sql_classifier.id}_{sql_classifier.name}"] = sql_classifier.id
    return clf_dict

# Update


def update_image_bg_false(uid: int, sess: Session = None):
    '''
    Expects image uid. Sets the image's "has_bg_layer" property to False and the "bg_layer_id" property to None.

    Parameters: 

        - uid(int): Valid image ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == uid).one()
    sql_image.has_bg_layer = False
    sql_image.bg_layer_id = None
    sess.commit()


def update_image_bg_true(uid: int, layer_uid: int, sess: Session = None):
    '''
    Expects image uid and layer uid. Sets the image's "has_bg_layer" property to True and the "bg_layer_id" property to the given layer uid.

    Parameters: 

        - uid(int): Valid image ID.
        - layer_uid(int): Valid layer ID.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == uid).one()
    sql_image.has_bg_layer = True
    sql_image.bg_layer_id = layer_uid
    sess.commit()


def update_image_hint(uid: int, new_hint: str, sess: Session = None):
    '''
    Function expects image id as int and new hint as string. Queries db for image and updates the hint.

    Parameters: 

        - uid(int): Valid image ID.
        - new_hint(str): String to be saved as hint.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == uid).one()
    sql_image.hint = new_hint
    sess.commit()


def update_experiment_name(uid: int, new_name: str, sess: Session = None):
    '''
    Function expects experiment id as int and new name as string. Queries db for experiment and updates the name.

    Parameters: 

        - uid(int): Valid experiment ID.
        - new_name(str): String to be saved as new name.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment = sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == uid).one()
    sql_experiment.name = new_name
    sess.commit()


def update_experiment_hint(uid: int, new_hint: str, sess: Session = None):
    '''
    Function expects experiment id as int and new name as string. Queries db for experiment and updates the hint.

    Parameters: 

        - uid(int): Valid experiment ID.
        - new_hint(str): String to be saved as new name.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment = sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == uid).one()
    sql_experiment.hint = new_hint
    sess.commit()


def update_experiment_description(uid: int, new_description: str, sess: Session = None):
    '''
    Function expects experiment id as int and new name as string. Queries db for experiment and updates the description.

    Parameters: 

        - uid(int): Valid experiment ID.
        - new_description(str): String to be saved as new description.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment = sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == uid).one()
    sql_experiment.description = new_description
    sess.commit()


def update_experiment_group_name(uid: int, new_name: str, sess: Session = None):
    '''
    Function expects experiment group id as int and new name as string. Queries db for experiment group and updates the name.

    Parameters: 

        - uid(int): Valid experiment group ID.
        - new_name(str): String to be saved.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    sql_experiment_group.name = new_name
    sess.commit()


def update_experiment_group_hint(uid: int, new_hint: str, sess: Session = None):
    '''
    Function expects experiment group id as int and new name as string. Queries db for experiment group and updates the name.

    Parameters: 

        - uid(int): Valid experiment group ID.
        - new_name(str): String to be saved.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    sql_experiment_group.hint = new_hint
    sess.commit()


def update_experiment_group_description(uid: int, new_description: str, sess: Session = None):
    '''
    Function expects experiment group id as int and new_description as string. Queries db for experiment group and updates the description property.

    Parameters: 

        - uid(int): Valid experiment group ID.
        - new_description(str): String to be saved.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    sql_experiment_group.description = new_description
    sess.commit()


def update_experiment_group_images(uid: int, image_id_list: List[int], sess: Session = None):
    '''
    Function expects experiment group id as int and a list of image ids. Queries db for experiment group and updates assosciated images.

    Parameters: 

        - uid(int): Valid experiment group ID.
        - image_id_list(List[int]): List of image ids to be added to the group.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == uid).one()
    sql_image_list = []
    for image_id in image_id_list:
        sql_image = sess.query(db_models.Image).filter(
            db_models.Image.id == image_id).one()
        sql_image_list.append(sql_image)
    sql_experiment_group.images.extend(sql_image_list)
    sess.commit()


def add_image_to_experiment_group(experiment_group, image_uid: int, sess: Session = None):
    '''
    Function expects an int experiment group object and a image id. Queries db for image and updates adds it to experiment group.
    Returns updated db_image

    Parameters: 

        - experiment_group(app.api.classes_internal.IntExperimentGroup): IntExperimentGroup Object.
        - image_uid(int): Image id to be added to the group.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == image_uid).one()
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group.uid).one()
    sql_experiment_group.images.append(sql_image)
    sess.commit()
    sess.refresh(sql_image)
    db_image = utils_db.image_sql_to_db(sql_image)
    return db_image


def add_result_layer_to_experiment_group(experiment_group, result_layer_uid: int, sess: Session = None):
    '''
    Function expects an int experiment group object and a result_layer id. Queries db for result layer and adds it to experiment group.

    Parameters: 

        - experiment_group(app.api.classes_internal.IntExperimentGroup): IntExperimentGroup Object.
        - result_layer_uid(int): result_layer_uid to be added to the group.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_layer = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == result_layer_uid).one()
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group.uid).one()
    sql_experiment_group.result_layers.append(sql_layer)
    sess.commit()


def add_measurement_to_experiment_group(experiment_group, measurement_uid: int, sess: Session = None):
    '''
    Function expects an int experiment group object and a measurement_uid. Queries db for measurement and adds it to experiment group.

    Parameters: 

        - experiment_group(app.api.classes_internal.IntExperimentGroup): IntExperimentGroup Object.
        - measurement_uid(int): measurement_uid to be added to the group.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_measurement = sess.query(db_models.Measurement).filter(
        db_models.Measurement.id == measurement_uid).one()
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group.uid).one()
    sql_experiment_group.measurements.append(sql_measurement)
    sess.commit()


def update_result_layer_hint(result_layer_uid: int, new_hint: str, sess: Session = None):
    '''
    Function expects an int experiment group object and a measurement_uid. Queries db for measurement and adds it to experiment group.

    Parameters: 

        - result_layer_uid(int): id of result_layer to be updated.
        - new_hint(str): string to be saved.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_layer = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == result_layer_uid).one()
    sql_layer.hint = new_hint
    sess.commit()


def update_result_layer_name(result_layer_uid: int, new_name: str, sess: Session = None):
    '''
    Function expects an int experiment group object and a measurement_uid. Queries db for measurement and adds it to experiment group.

    Parameters: 

        - result_layer_uid(int): id of result_layer to be updated.
        - new_name(str): string to be saved.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_layer = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == result_layer_uid).one()
    sql_layer.name = new_name
    sess.commit()


def update_classifier_name(classifier_uid: int, new_name: str, sess: Session = None):
    '''
    Function expects an int experiment group object and a measurement_uid. Queries db for measurement and adds it to experiment group.

    Parameters: 

        - classifier_uid(int): id of classifier to be updated.
        - new_name(str): string to be saved.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_clf = sess.query(db_models.Classifier).filter(
        db_models.Classifier.id == classifier_uid).one()
    sql_clf.name = new_name
    sess.commit()

# Delete


def delete_result_layer(db_layer, sess: Session = None):
    '''
    Expects a c_db.DbResultLayer object. Deletes all associated measurements and the layer itself.

    Parameters: 

        - db_layer(app.api.classes_db.DbResultLayer): object to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    result_layer_uid = db_layer.uid
    q = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == result_layer_uid)
    sql_layer = q.one()
    for measurement in sql_layer.measurements:
        fsr.delete_file(measurement.path)
        fsr.delete_file(measurement.path_summary)
        sess.query(db_models.Measurement).filter(
            db_models.Measurement.id == measurement.id).delete()
        sess.commit()
    fsr.delete_folder(sql_layer.path)
    q.delete()
    sess.commit()


def delete_image(db_image, sess: Session = None):
    '''
    Expects a c_db.DbImage object. Deletes all associated layers and results, then deletes image + Metadata

    Parameters: 

        - db_image(app.api.classes_db.DbImage): object to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    for layer in db_image.image_result_layers:
        layer.delete()
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == db_image.uid).one()
    sql_image.experiment_groups = []
    sess.commit()
    sess.refresh(sql_image)
    sess.delete(sql_image)
    sess.commit()
    fsr.delete_folder(db_image.path_image)
    fsr.delete_file(db_image.path_metadata)
    fsr.delete_file(utils_paths.fileserver.joinpath(
        utils_paths.make_thumbnail_path(db_image.uid)))
    fsr.delete_file(utils_paths.make_metadata_xml_path_from_json_path(
        db_image.path_metadata))


def remove_image_from_experiment_group(experiment_group, image_uid: int, sess: Session = None):
    '''
    Expects a experiment_group object (db/com/int are possible since only the uid property is read). Removes image from experiment group.

    Parameters: 

        - experiment_group(app.api.classes_db.DbImage): group from which the image should be removed.
        - image_uid(int): uid of image to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_image = sess.query(db_models.Image).filter(
        db_models.Image.id == image_uid).one()
    result_layers = sql_image.result_layers
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group.uid).one()
    for result_layer in result_layers:
        if result_layer in sql_experiment_group.result_layers:
            sql_experiment_group.result_layers.remove(result_layer)
    sql_experiment_group.images.remove(sql_image)
    sess.commit()


def remove_result_layer_from_experiment_group(experiment_group, result_layer_uid: int, sess: Session = None):
    '''
    Expects a experiment_group object (db/com/int are possible since only the uid property is read). Removes result layer from experiment group.

    Parameters: 

        - experiment_group(app.api.classes_db.DbImage): group from which the image should be removed.
        - result_layer_uid(int): uid of result_layer to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_layer = sess.query(db_models.ResultLayer).filter(
        db_models.ResultLayer.id == result_layer_uid).one()
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group.uid).one()
    sql_experiment_group.result_layers.remove(sql_layer)
    sess.commit()


def remove_measurement_from_experiment_group(experiment_group, measurement_uid: int, sess: Session = None):
    '''
    Expects a experiment_group object (db/com/int are possible since only the uid property is read). Removes measurement from experiment group.

    Parameters: 

        - experiment_group(app.api.classes_db.DbImage): group from which the image should be removed.
        - measurement_uid(int): uid of measurement to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_measurement = sess.query(db_models.Measurement).filter(
        db_models.Measurement.id == measurement_uid).one()
    sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group.uid).one()
    sql_experiment_group.measurements.remove(sql_measurement)
    sess.commit()


def delete_classifier(clf, sess: Session = None):
    '''
    Expects classifier (c_db) and deletes it from database as well as file storage.

    Parameters: 

        - clf(app.api.classes_db.DbClassifier): Classifier to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sess.query(db_models.Classifier).filter(
        db_models.Classifier.id == clf.uid).delete()
    sess.commit()
    if clf.clf_type == "rf_segmentation":
        fsr.delete_file(clf.path_clf)
        fsr.delete_file(clf.path_test_train)
    if clf.clf_type == "deepflash_model":
        fsr.delete_folder(clf.path_clf)


def delete_experiment_result(experiment_result_uid: int, sess: Session = None):
    '''
    Expects uid of experiment result, deletes it from db and filesserver.

    Parameters: 

        - experiment_result_uid(int): uid of experiment result to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_result = sess.query(db_models.ExperimentResult).filter(
        db_models.ExperimentResult.id == experiment_result_uid).one()
    fsr.delete_file(sql_result.path)
    sess.query(db_models.ExperimentResult).filter(
        db_models.ExperimentResult.id == experiment_result_uid).delete()
    sess.commit()


def delete_experiment_group_by_id(experiment_group_uid: int, sess: Session = None):
    '''
    Expects a experiment_group_id as int, queries db for experiment_group, deletes experiment_group.3

    Parameters: 

        - experiment_group_id(int): uid of experiment group to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_group = sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group_uid).one()
    sql_group.images = []
    sql_group.result_layers = []
    sess.commit()
    sess.refresh(sql_group)
    if sql_group.experiment_result:
        delete_experiment_result(sql_group.experiment_result.id)
    sess.query(db_models.ExperimentGroup).filter(
        db_models.ExperimentGroup.id == experiment_group_uid).delete()
    sess.commit()


def delete_experiment_by_id(experiment_uid: int, sess: Session = None):
    '''
    Expects a experiment_id as int, queries db for experiment, deletes experiment.

    Parameters: 

        - experiment_uid(int): uid of experiment to be deleted.
        - sess(sqlalchemy.orm.Session): The database session to be used.
    '''
    sess = check_sess(sess)
    sql_exp = sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == experiment_uid).one()
    for group in sql_exp.experiment_groups:
        delete_experiment_group_by_id(group.id)
        sess.commit()
    sess.query(db_models.Experiment).filter(
        db_models.Experiment.id == experiment_uid).delete()
    sess.commit()
