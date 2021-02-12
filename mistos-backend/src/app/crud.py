from app.database import engine
from . import db_models
from sqlalchemy.orm import Session
from app.database import SessionLocal

import app.api.utils_paths as utils_paths
import app.api.utils_db as utils_db
import app.fileserver_requests as fsr

# Create
def create_image(image): 
    # if expire_on_commit == False, we can access objects after a session is closes
    # objects will not be in sync with db
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = db_models.Image(
            name = image.name,
            series_index = image.series_index,
            hint = image.hint,
            tags = image.tags,
            has_bg_layer = image.has_bg_layer,
            bg_layer_id = image.bg_layer_id
        )
        sess.add(sql_image)
        sess.commit()
        sess.refresh(sql_image)
        sql_image.path_image = utils_paths.fileserver.joinpath(utils_paths.make_image_path(sql_image.id)).as_posix()
        sql_image.path_metadata = utils_paths.fileserver.joinpath(utils_paths.make_metadata_path(sql_image.id)).as_posix()
        sess.commit()

        return sql_image

def create_result_layer(result_layer): 
    with SessionLocal(expire_on_commit = False) as sess:
        sql_layer = db_models.ResultLayer(
            name = result_layer.name,
            hint = result_layer.hint,
            layer_type = result_layer.layer_type,
            image_id = result_layer.image_id
        )
        sess.add(sql_layer)
        sess.commit()
        sql_layer.path = utils_paths.fileserver.joinpath(utils_paths.make_result_layer_path(sql_layer.id)).as_posix()
        sess.commit()

        return sql_layer

def create_experiment_group(experiment_group):
    with SessionLocal(expire_on_commit = False) as sess:
        experiment = sess.query(db_models.Experiment).filter(db_models.Experiment.id == experiment_group.experiment_id).one()
        
        sql_group = db_models.ExperimentGroup(
            name = experiment_group.name,
            hint = experiment_group.hint,
            description = experiment_group.description,
            experiment = experiment
        )
        sess.add(sql_group)
        sess.commit()

        return sql_group

def create_experiment_result(experiment_result):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_result.experiment_group_id).one()
        
        sql_result = db_models.ExperimentResult(
            name = experiment_result.name,
            hint = experiment_result.hint,
            description = experiment_result.description,
            result_type = experiment_result.result_type,
            experiment_group = sql_experiment_group
        )
        sess.add(sql_result)
        sess.commit()
        sess.refresh(sql_result)

        sql_result.path = utils_paths.fileserver.joinpath(utils_paths.make_result_path(sql_result.id)).as_posix()
        sess.commit()

        return sql_result

def create_experiment(experiment):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_experiment = db_models.Experiment(
            name = experiment.name,
            hint = experiment.hint,
            description = experiment.description,
            tags = experiment.tags
        )
        sess.add(sql_experiment)
        sess.commit()

        return sql_experiment

def create_result_measurement(result_measurement):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == result_measurement.image_id).one()
        sql_result_layer = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == result_measurement.result_layer_id).one()
        
        sql_measurement = db_models.Measurement(
            name = result_measurement.name,
            hint = result_measurement.hint,
            # path = result_measurement.path,
        )

        sql_image.measurements.append(sql_measurement)
        sql_result_layer.measurements.append(sql_measurement)

        sess.add(sql_measurement)
        sess.commit()
        sess.refresh(sql_measurement)
        sql_measurement.path = utils_paths.fileserver.joinpath(utils_paths.make_measurement_path(sql_measurement.id)).as_posix()
        sql_measurement.path_summary = utils_paths.fileserver.joinpath(utils_paths.make_measurement_summary_path(sql_measurement.id)).as_posix()
        sess.commit()

        return sql_measurement

def create_classifier(classifier):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_clf = db_models.Classifier(
            name = classifier.name,
            clf_type = classifier.clf_type,
            params = classifier.params,
            metrics = classifier.metrics,
            tags = classifier.tags
        )

        sess.add(sql_clf)
        sess.commit()
        sess.refresh(sql_clf)

        sql_clf.path_clf = utils_paths.fileserver.joinpath(utils_paths.make_clf_path(sql_clf.id)).as_posix()
        sql_clf.path_test_train = utils_paths.fileserver.joinpath(utils_paths.make_clf_test_train_path(sql_clf.id)).as_posix()

        sess.commit()
        return sql_clf

#  Read
def read_image_by_uid(uid, for_refresh = False):
    '''
    Expects image uid and returns c_int.IntImage object.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        db_image = utils_db.image_sql_to_db(sql_image)
        c_int_image = db_image.to_int_class(for_refresh)
        return c_int_image

def read_db_image_by_uid(uid, for_refresh = False):
    '''
    Expects image uid and returns c_db.DbImage object.
    '''
    with SessionLocal() as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        db_image = utils_db.image_sql_to_db(sql_image)
        return db_image

def read_all_images():
    '''
    Fetches all images from db and returns them as list of DbImage objects.
    '''
    with SessionLocal() as sess:
        sql_image_list = sess.query(db_models.Image)
        db_image_list = [utils_db.image_sql_to_db(sql_image) for sql_image in sql_image_list]
    return db_image_list

def read_all_classifiers():
    '''
    This function fetches all classifiers from the db and returns them as list of DbClassifier objects.
    '''
    with SessionLocal() as sess:
        sql_clf_list = sess.query(db_models.Classifier)
        db_clf_list = [utils_db.classifier_sql_to_db(sql_clf) for sql_clf in sql_clf_list]
    return db_clf_list

def read_db_classifier_by_uid(uid, for_refresh = False):
    '''
    Expects classifier uid and returns c_db.DbClassifier object.
    '''
    with SessionLocal() as sess:
        sql_clf = sess.query(db_models.Classifier).filter(db_models.Classifier.id == uid).one()
        sql_clf = utils_db.classifier_sql_to_db(sql_clf)
        return sql_clf

def read_all_experiments():
    '''
    This function fetches all experiments from the db and returns them as list of DbExperiment objects.
    '''
    with SessionLocal() as sess:
        sql_exp_list = sess.query(db_models.Experiment)
        db_exp_list = [utils_db.experiment_sql_to_db(sql_exp) for sql_exp in sql_exp_list]
    return db_exp_list

def read_experiment_by_uid(uid):
    '''
    Expects experiment uid and returns c_db.DbExperiment object
    '''
    with SessionLocal() as sess:
        sql_experiment = sess.query(db_models.Experiment).filter(db_models.Experiment.id == uid).one()
        db_experiment = utils_db.experiment_sql_to_db(sql_experiment)
        return db_experiment

def read_experiment_group_by_uid(uid, for_refresh = False):
    '''
    Expects experiment_group uid and returns c_int.IntExperimentGroup object.
    '''
    with SessionLocal(expire_on_commit = True) as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
        db_experiment_group = utils_db.experiment_group_sql_to_db(sql_experiment_group)
        c_int_experiment_group = db_experiment_group.to_int_class(for_refresh)
        return c_int_experiment_group

def read_experiment_db_group_by_uid(uid, for_refresh = False):
    '''
    Expects experiment_group uid and returns c_db.DbExperimentGroup object.
    '''
    with SessionLocal(expire_on_commit = True) as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
        db_experiment_group = utils_db.experiment_group_sql_to_db(sql_experiment_group)
        return db_experiment_group

def read_result_of_experiment_group_by_id(uid):
    '''
    Expects uid of experiment group, returns the groups' result as c_db.DbExperimentResultObject
    '''
    with SessionLocal() as sess:
        sql_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
        print(sql_group)

        return utils_db.experiment_result_sql_to_db(sql_group.experiment_result)

def read_result_layers_of_image_uid(uid):
    '''
    Expects image uid and returns a list of c_db.DbResultLayer objects.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        sql_result_layers = sql_image.result_layers
        db_result_layers = [utils_db.result_layer_sql_to_db(sql_result_layer) for sql_result_layer in sql_result_layers]

        return c_int_image

def read_result_layer_by_uid(uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_layer = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid).one()
        
        return utils_db.result_layer_sql_to_db(sql_layer)

def read_measurement_by_result_layer_uid(uid):
    '''
    Expects a result layer uid and returns a db_measurement object.
    '''
    with SessionLocal() as sess:
        sql_measurement = sess.query(db_models.Measurement).filter(db_models.Measurement.result_layer_id == uid).one()
        db_measurement = utils_db.measurement_sql_to_db(sql_measurement)
        return db_measurement

def read_classifier_by_uid(uid):
    '''
    Expects classifier uid and returns c_int.IntClassifier object.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_classifier = sess.query(db_models.Classifier).filter(db_models.Classifier.id == uid).one()
        db_classifier = utils_db.classifier_sql_to_db(sql_classifier)
        c_int_classifier = db_classifier.to_int_class()
        return c_int_classifier

def read_classifier_dict_by_type(clf_type):
    '''
    Expects clf_type as string as defined in utils_db and returns a dict of {name: id}.
    '''
    with SessionLocal() as sess:
        sql_classifiers = sess.query(db_models.Classifier).filter(db_models.Classifier.clf_type == clf_type)

        clf_dict = {}
        for sql_classifier in sql_classifiers:
            clf_dict[f"{sql_classifier.id}_{sql_classifier.name}"] = sql_classifier.id


        return clf_dict

# Update
def update_image_bg_false(uid):
    with SessionLocal() as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        sql_image.has_bg_layer = False
        sql_image.bg_layer_id = None
        sess.commit()

def update_image_bg_true(uid, layer_uid):
    with SessionLocal() as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        sql_image.has_bg_layer = True
        sql_image.bg_layer_id = layer_uid
        sess.commit()

def update_image_hint(uid, new_hint):
    '''
    Function expects image id as int and new hint as string. Queries db for image and updates the hint
    '''
    with SessionLocal() as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        sql_image.hint = new_hint
        sess.commit()

def update_experiment_name(uid, new_name):
    with SessionLocal() as sess:
        sql_experiment = sess.query(db_models.Experiment).filter(db_models.Experiment.id == uid).one()
        sql_experiment.name = new_name
        sess.commit()

def update_experiment_hint(uid:int, new_hint:str):
    with SessionLocal() as sess:
        sql_experiment = sess.query(db_models.Experiment).filter(db_models.Experiment.id == uid).one()
        sql_experiment.hint = new_hint
        sess.commit()

def update_experiment_description(uid:int, new_description:str):
    with SessionLocal() as sess:
        sql_experiment = sess.query(db_models.Experiment).filter(db_models.Experiment.id == uid).one()
        sql_experiment.description = new_description
        sess.commit()

def update_experiment_group_name(uid, new_name):
        with SessionLocal() as sess:
            sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
            sql_experiment_group.name = new_name
            sess.commit()

def update_experiment_group_hint(uid:int, new_hint:str):
    with SessionLocal() as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
        sql_experiment_group.hint = new_hint
        sess.commit()

def update_experiment_group_description(uid:int, new_description:str):
    with SessionLocal() as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
        sql_experiment_group.description = new_description
        sess.commit()

def update_experiment_group_images(uid:int, image_id_list):
    with SessionLocal() as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()

        sql_image_list = []
        for image_id in image_id_list:
            sql_image = sess.query(db_models.Image).filter(db_models.Image.id == image_id).one()
            sql_image_list.append(sql_image)
        sql_experiment_group.images.extend(sql_image_list)
        sess.commit()

def add_image_to_experiment_group(experiment_group, image_uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == image_uid).one()
        sql_image
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.images.append(sql_image)
        sess.commit()

        db_image = utils_db.image_sql_to_db(sql_image)

        return db_image

def add_result_layer_to_experiment_group(experiment_group, uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_layer = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid).one()
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.result_layers.append(sql_layer)

        sess.commit()

def add_measurement_to_experiment_group(experiment_group, uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_measurement = sess.query(db_models.Measurement).filter(db_models.Measurement.id == uid).one()
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.measurements.append(sql_measurement)

        sess.commit()

def update_result_layer_hint(uid:int, new_hint:str):
    with SessionLocal() as sess:
        sql_layer = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid).one()
        sql_layer.hint = new_hint
        sess.commit()

def update_result_layer_name(uid:int, new_name:str):
    with SessionLocal() as sess:
        sql_layer = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid).one()
        sql_layer.name = new_name
        sess.commit()

# Delete
def delete_result_layer(db_layer):
    '''
    Expects a c_db.DbResultLayer object. Deletes all associated measurements and the layer itself.
    '''
    uid = db_layer.uid

    with SessionLocal() as sess:
        q = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid)
        sql_layer = q.one()

        for measurement in sql_layer.measurements:
            fsr.delete_folder(measurement.path)
            fsr.delete_file(measurement.path_summary)
            layer_query = sess.query(db_models.Measurement).filter(db_models.Measurement.id == measurement.id).delete()
            sess.commit()

        fsr.delete_folder(sql_layer.path)

        q.delete()
        sess.commit()

def delete_image(db_image):
    '''
    Expects a c_db.DbImage object. Deletes all associated layers and results, then deletes image + Metadata
    '''
    for layer in db_image.image_result_layers:
        layer.delete()

    with SessionLocal() as sess:
        q = sess.query(db_models.Image).filter(db_models.Image.id == db_image.uid)
        sql_image = q.one()
        q.delete()
        sess.commit()

    fsr.delete_folder(db_image.path_image)
    fsr.delete_file(db_image.path_metadata)
    fsr.delete_file(db_image.path_metadata.replace(".json", ".xml"))

def remove_image_from_experiment_group(experiment_group, image_uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == image_uid).one()
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.images.remove(sql_image)
        sess.commit()

def remove_result_layer_from_experiment_group(experiment_group, uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_layer = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid).one()
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.result_layers.remove(sql_layer)

        sess.commit()

def remove_measurement_from_experiment_group(experiment_group, uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_measurement = sess.query(db_models.Measurement).filter(db_models.Measurement.id == uid).one()
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.measurements.remove(sql_measurement)

        sess.commit()

def delete_experiment_result(uid):
    '''
    Expects uid of experiment result, deletes it from db and filesserver.
    '''
    with SessionLocal() as sess:
        sql_result = sess.query(db_models.ExperimentResult).filter(db_models.ExperimentResult.id == uid).one()
        fsr.delete_file(sql_result.path)
        sess.query(db_models.ExperimentResult).filter(db_models.ExperimentResult.id == uid).delete()
        sess.commit()


def delete_experiment_group_by_id(experiment_group_id: int):
    '''
    Expects a experiment_group_id as int, queries db for experiment_group, deletes experiment_group.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group_id).one()
        delete_experiment_result(sql_group.experiment_result.id)

        sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group_id).delete()
        sess.commit()

def delete_experiment_by_id(experiment_id: int):
    '''
    Expects a experiment_id as int, queries db for experiment, deletes experiment.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_exp = sess.query(db_models.Experiment).filter(db_models.Experiment.id == experiment_id).one()
        for group in sql_exp.experiment_groups:
            delete_experiment_group_by_id(group.id)
            sess.commit()

        sess.query(db_models.Experiment).filter(db_models.Experiment.id == experiment_id).delete()
        sess.commit()