from app.database import engine
from . import db_models
from sqlalchemy.orm import Session
from app.database import SessionLocal

import app.api.utils_paths as utils_paths
import app.api.classes_db as c_db
import app.api.utils_classes as utils_classes
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
        sql_result = db_models.ExperimentResult(
            name = experiment_result.name,
            hint = experiment_result.hint,
            description = experiment_result.description,
            result_type = experiment_result.result_type,
        )
        sess.add(sql_result)
        sess.commit()

        sql_result.path = utils_paths.make_result_path(sql_result.id)
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
            path = result_measurement.path
        )

        sql_image.measurements.append(sql_measurement)
        sql_result_layer.measurements.append(sql_measurement)

        sess.add(sql_measurement)
        sess.commit()
        sess.refresh(sql_measurement)
        sql_measurement.path = utils_paths.fileserver.joinpath(utils_paths.make_measurement_path(sql_measurement.id)).as_posix()
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
        db_image = utils_classes.image_sql_to_db(sql_image)
        c_int_image = db_image.to_int_class(for_refresh)
        return c_int_image

def read_experiment_group_by_uid(uid, for_refresh = False):
    '''
    Expects experiment_group uid and returns c_int.IntExperimentGroup object.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == uid).one()
        db_experiment_group = utils_classes.experiment_group_sql_to_db(sql_experiment_group)
        c_int_experiment_group = db_experiment_group.to_int_class(for_refresh)
        return c_int_experiment_group

def read_result_layers_of_image_uid(uid):
    '''
    Expects image uid and returns a list of c_db.DbResultLayer objects.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == uid).one()
        sql_result_layers = sql_image.result_layers
        db_result_layers = [utils_classes(sql_result_layer) for sql_result_layer in sql_result_layers]

        return c_int_image

def read_classifier_by_uid(uid):
    '''
    Expects classifier uid and returns c_int.IntClassifier object.
    '''
    with SessionLocal(expire_on_commit = False) as sess:
        sql_classifier = sess.query(db_models.Classifier).filter(db_models.Classifier.id == uid).one()
        db_classifier = utils_classes.classifier_sql_to_db(sql_classifier)
        c_int_classifier = db_classifier.to_int_class()
        return c_int_classifier

def read_classifier_dict_by_type(clf_type):
    '''
    Expects clf_type as string as defined in utils_classes and returns a dict of {name: id}.
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

def add_image_to_experiment_group(experiment_group, image_uid):
    with SessionLocal(expire_on_commit = False) as sess:
        sql_image = sess.query(db_models.Image).filter(db_models.Image.id == image_uid).one()
        sql_image
        sql_experiment_group = sess.query(db_models.ExperimentGroup).filter(db_models.ExperimentGroup.id == experiment_group.uid).one()

        sql_experiment_group.images.append(sql_image)
        sess.commit()

        db_image = utils_classes.image_sql_to_db(sql_image)

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

# Delete
def delete_result_layer(db_layer: c_db.DbImageResultLayer):
    '''
    Expects a c_db.DbResultLayer object. Deletes all associated measurements and the layer itself.
    '''
    uid = db_layer.uid

    with SessionLocal() as sess:
        q = sess.query(db_models.ResultLayer).filter(db_models.ResultLayer.id == uid)
        sql_layer = q.one()

        for measurement in sql_layer.measurements:
            fsr.delete_file(measurement.path)

        fsr.delete_folder(sql_layer.path)

        q.delete()
        sess.commit()

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