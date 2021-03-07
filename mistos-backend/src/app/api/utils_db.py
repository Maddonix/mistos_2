import app.api.classes_db as c_db


def experiment_result_sql_to_db(sql_experiment_group):
    kwargs = {
        "uid": sql_experiment_group.id,
        "name": sql_experiment_group.name,
        "hint": sql_experiment_group.hint,
        "description": sql_experiment_group.description,
        "experiment_group_id": sql_experiment_group.experiment_group_id,
        "result_type": sql_experiment_group.result_type,
        "path": sql_experiment_group.path
    }

    return c_db.DbExperimentResult(**kwargs)


def measurement_sql_to_db(sql_measurement):
    kwargs = {
        "uid": sql_measurement.id,
        "name": sql_measurement.name,
        "path": sql_measurement.path,
        "path_summary": sql_measurement.path_summary,
        "hint": sql_measurement.hint,
        "image_id": sql_measurement.image_id,
        "result_layer_id": sql_measurement.result_layer_id
    }

    return c_db.DbResultMeasurement(**kwargs)


def result_layer_sql_to_db(sql_result_layer):
    kwargs = {
        "uid": sql_result_layer.id,
        "name": sql_result_layer.name,
        "hint": sql_result_layer.hint,
        "path": sql_result_layer.path,
        "image_id": sql_result_layer.image_id,
        "layer_type": sql_result_layer.layer_type
    }

    return c_db.DbImageResultLayer(**kwargs)


def image_sql_to_db(sql_image):
    result_layers = [result_layer_sql_to_db(
        result_layer) for result_layer in sql_image.result_layers]
    measurements = [measurement_sql_to_db(
        measurement) for measurement in sql_image.measurements]

    kwargs = {
        "uid": sql_image.id,
        "series_index": sql_image.series_index,
        "name": sql_image.name,
        "hint": sql_image.hint,
        "path_metadata": sql_image.path_metadata,
        "path_image": sql_image.path_image,
        "image_result_layers": result_layers,
        "measurements": measurements,
        "tags": sql_image.tags,
        "has_bg_layer": sql_image.has_bg_layer,
        "bg_layer_id": sql_image.bg_layer_id
    }
    db_image = c_db.DbImage(**kwargs)

    return db_image


def experiment_group_sql_to_db(sql_experiment_group):
    images = [image_sql_to_db(img) for img in sql_experiment_group.images]
    result_layer_ids = [r.id for r in sql_experiment_group.result_layers]
    measurement_ids = [m.id for m in sql_experiment_group.measurements]

    kwargs = {
        "uid": sql_experiment_group.id,
        "name": sql_experiment_group.name,
        "hint": sql_experiment_group.hint,
        "experiment_id": sql_experiment_group.experiment_id,
        "description": sql_experiment_group.description,
        "images": images,
        "result_layer_ids": result_layer_ids,
        "measurement_ids": measurement_ids
    }

    return c_db.DbExperimentGroup(**kwargs)


def experiment_sql_to_db(sql_experiment):
    '''
    This function expects a sql_experiment object and returns a db_experiment object
    '''
    experiment_groups = [experiment_group_sql_to_db(
        exp_g) for exp_g in sql_experiment.experiment_groups]
    kwargs = {
        "uid": sql_experiment.id,
        "name": sql_experiment.name,
        "hint": sql_experiment.hint,
        "description": sql_experiment.description,
        "tags": sql_experiment.tags,
        "experiment_groups": experiment_groups
    }

    return c_db.DbExperiment(**kwargs)


def classifier_sql_to_db(sql_classifier):

    kwargs = {
        "uid": sql_classifier.id,
        "name": sql_classifier.name,
        "clf_type": sql_classifier.clf_type,
        "path_clf": sql_classifier.path_clf,
        "path_test_train": sql_classifier.path_test_train,
        "params": sql_classifier.params,
        "metrics": sql_classifier.metrics,
        "tags": sql_classifier.tags
    }

    # Try to remove if real data in db
    if kwargs["metrics"] == None:
        kwargs["metrics"] = {}
    if kwargs["params"] == None:
        kwargs["params"] = {}

    return c_db.DbClassifier(**kwargs)
