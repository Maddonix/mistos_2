# pylint:disable=no-name-in-module
from pydantic import BaseModel, constr
from typing import List, Optional, Set, Any
import numpy as np
import pandas as pd
import copy

from app import crud
import app.api.cfg_classes as cfg_classes
import app.api.classes_db as c_db
import app.api.utils_import as utils_import
from app.api import utils_paths, utils_results, utils_export, utils_transformations
from app.api.cfg_classes import channel_measurement_tuple
from app import fileserver_requests as fsr


class IntImageResultLayer(BaseModel):
    uid: int
    name: str
    hint: Optional[str] = ""
    image_id: int
    layer_type: constr(regex=cfg_classes.layer_type_regex)
    data: Any

    def on_init(self):
        # should be called on every creation
        if self.uid == -1:
            if len(self.data.shape) == 2:
                print(
                    f"WARNING: Result Layer was initialized with shape {self.data.shape}, appending new axis to match universal layer shape (z,y,x)")
                self.data = self.data[np.newaxis, ...]
            assert len(self.data.shape) == 3
            print("On Init IntImageResultLayer:")
            db_layer = self.to_db_class()
            db_layer.create_in_db()
            self.uid = db_layer.uid

            self.data = self.data.astype(int)

            print(f"New Layer created with id {self.uid}")
            utils_import.save_label_layer_to_zarr(
                array=self.data,
                filepath=db_layer.path
            )

    def delete(self):
        '''
        This function removes a result_layer as well as the associated measurements
        '''
        db_layer = self.to_db_class()
        db_layer.delete()

    def to_db_class(self):
        '''
        Transforms internal class representation to db class representation.
        '''

        args = self.dict()
        del args["data"]
        db_image_result_layer = c_db.DbImageResultLayer(**args)

        return db_image_result_layer


class IntResultMeasurement(BaseModel):
    '''
    Class to store and work with Measurements.
    IntResultMeasurement.measurement is a dict
    '''
    uid: int
    name: str
    hint: str = ""
    image_id: int
    result_layer_id: int
    measurement: Any
    measurement_summary: Any

    def on_init(self):
        if self.uid == -1:
            print("On Init IntResultMeasurement")
            db_result_measurement = self.to_db_class()
            db_result_measurement.create_in_db()

            self.uid = db_result_measurement.uid
            self.save_measurement(db_result_measurement.path,
                                  db_result_measurement.path_summary)

    def to_db_class(self):
        kwargs = self.dict()
        del kwargs["measurement"]
        del kwargs["measurement_summary"]
        db_result_measurement = c_db.DbResultMeasurement(**kwargs)
        return db_result_measurement

    def save_measurement(self, path, path_summary):
        fsr.save_measurement(self.measurement, path)
        fsr.save_measurement_summary(self.measurement_summary, path_summary)


class IntImage(BaseModel):
    uid: int
    name: str
    series_index: int
    metadata: dict
    hint: Optional[str] = ""
    experiment_ids: List[int] = []
    image_result_layers: List[IntImageResultLayer] = []
    result_measurements: List[IntResultMeasurement] = []
    tags: Set[str] = set()
    data: Any
    metadata_omexml: Any
    has_bg_layer: bool = False
    bg_layer_id: Optional[int]

    def on_init(self):
        '''
        On Init method should be called after image is created.
        Image will be saved to db and file storage.
        Image must have uid -1 (completely new image) or uid -2 (importing archived mistos image)
        '''
        if self.uid == -1:
            print("On Init Image:")
            db_image = self.to_db_class()
            db_image.create_in_db()
            self.uid = db_image.uid

            print(f"New Image created with id {self.uid}")
            utils_import.save_zarr(
                index=self.series_index,
                array=self.data,
                metadata_dict=self.metadata,
                metadata_omexml=self.metadata_omexml,
                filepath_zarr=db_image.path_image,
                filepath_metadata=db_image.path_metadata
            )

            thumbnail = utils_import.generate_thumbnail(self.data)
            thumbnail_path = self.get_thumbnail_path()

            fsr.save_thumbnail(thumbnail, thumbnail_path)

        elif self.uid == -2:
            print("Importing archived Mistos image")
            db_image = self.to_db_class()
            db_image.create_in_db()
            self.uid = db_image.uid

            fsr.save_zarr(self.data, db_image.path_image)
            fsr.save_json(self.metadata, db_image.path_metadata)

    def get_thumbnail_path(self):
        return utils_paths.fileserver.joinpath(utils_paths.make_thumbnail_path(self.uid)).as_posix()

    def get_image_scaling(self):
        '''
        Reads pixel dimensions and returns relative dimensions.
        Returns dimensions normalized scales in array with shape (z,y,x)
        '''
        x = self.metadata['pixel_size_physical_x']
        y = self.metadata['pixel_size_physical_y']
        z = self.metadata['pixel_size_physical_z']
        n_z = self.metadata['pixel_size_z']
        if n_z > 1:
            dims = np.array([z, y, x])
            dims = dims/dims.max()
        elif n_z == 1:
            dims = np.array([y, x])
            dims = dims/dims.max()
        else:
            dims = None
            print("Couldn't calculate scaling from metadata, defaulting to None")

        return dims

    def to_db_class(self):
        '''
        Transforms internal class representation to db class representation.
        '''
        db_image_result_layers = [result_layer.to_db_class()
                                  for result_layer in self.image_result_layers]
        db_result_measurements = [measurement.to_db_class()
                                  for measurement in self.result_measurements]

        db_image = c_db.DbImage(
            uid=self.uid,
            series_index=self.series_index,
            name=self.name,
            hint=self.hint,
            path_metadata=None,
            path_image=None,
            has_bg_layer=self.has_bg_layer,
            bg_layer_id=self.bg_layer_id,
            experiment_ids=self.experiment_ids,
            image_result_layers=db_image_result_layers,
            result_measurements=db_result_measurements,
            tags=self.tags
        )

        return db_image

    def set_bg_false(self):
        db_image = self.to_db_class()
        db_image.set_bg_false()

        self.refresh_from_db()

    def set_bg_true(self, image_layer: IntImageResultLayer):
        layer_uid = image_layer.uid
        db_image = self.to_db_class()
        db_image.set_bg_true(layer_uid)

    def select_channel(self, channel):
        channel_data = copy.deepcopy(self.data[:, channel, ...])
        return channel_data

    def select_result_layer(self, uid):
        layers = [_ for _ in self.image_result_layers if _.uid == uid]
        if len(layers) > 0:
            return layers[0]

    def calculate_background(self, all_channels=True):
        '''
        Expects the bg_uid to belong to a result layer of this image.
        Result layer must be binary.
        Returns list of len = n_channel with mean intensity of measured pixels.
        '''
        if self.has_bg_layer:
            print(self.bg_layer_id)
            bg_uid = self.bg_layer_id
            print([_.uid for _ in self.image_result_layers])
            bg_layer = self.select_result_layer(bg_uid)
            print(bg_layer)
            bg_mask = bg_layer.data
        else:
            bg_mask = np.zeros((
                self.data.shape[0],
                self.data.shape[2],
                self.data.shape[3]
            ))
        assert bg_mask.max() < 2
        n_pixel = bg_mask.sum()
        n_channel = self.data.shape[1]
        mean_pixel = []
        for n in range(n_channel):
            channel_data = self.select_channel(n)
            selection = np.where(bg_mask, channel_data, 0)
            _mean = selection.sum()/n_pixel
            mean_pixel.append(_mean)

        return mean_pixel

    def subtract_background(self, all_channels=True):
        bg_uid = self.bg_layer_id
        mean_bg_pixel_list = self.calculate_background()

        img_bgs = self.data

        for i, mean_pixel in enumerate(mean_bg_pixel_list):
            img_bgs[:, i, ...] = img_bgs[:, i, ...]-mean_pixel

        # pixels lower than 0 will be set to 0
        img_bgs[img_bgs < 0] = 0

        return img_bgs, mean_bg_pixel_list

    def measure_mask_in_image(self, layer_id):
        '''
        Expects a layer id.
        Creates measurement object and initializes it (save to db and file storage)
        Returns measurement object.
        measurement.measurement has shape: (n_labels, n_channel, n_features), n_features == 2 (n_pixels, sum_pixels)

        Keyword arguments:
        layer_id -- uid of the layer to be measured
        subtract_background -- if True, background will be subtracted before measuring. If no background layer is defined, this step is passed
        '''
        image_array = self.data
        layer = self.select_result_layer(layer_id)
        measurement, measurement_summary = utils_results.calculate_measurement(
            image_array, layer.data)

        measurement_result = IntResultMeasurement(
            uid=-1,
            name=utils_paths.make_measurement_name(self.name, layer.name),
            hint="",
            image_id=self.uid,
            result_layer_id=layer.uid,
            measurement=measurement,
            measurement_summary=measurement_summary
        )

        measurement_result.on_init()
        self.refresh_from_db()

        return measurement_result

    def get_classifiers(self, clf_type):
        # Fetches dict in form {name: id}
        clf_dict = crud.read_classifier_dict_by_type(clf_type)
        if clf_dict == {}:
            clf_dict["No classifers found"] = None
        return clf_dict

    def refresh_from_db(self):
        '''
        requests current information from db and updates the object, does not load image data again:
        - name: str
        - hint: Optional[str] = ""
        - experiment_ids: List[int] = []
        - image_result_layers: List[IntImageResultLayer] = []
        - tags: Set[str] = set()
        - has_bg_layer: bool = False
        - bg_layer_id: Optional[int]
        '''

        db_image = self.to_db_class()
        updated_info = db_image.refresh_from_db()

        self.name = updated_info.name
        self.hint = updated_info.hint
        self.experiment_ids = updated_info.experiment_ids
        self.image_result_layers = updated_info.image_result_layers
        self.result_measurements = updated_info.result_measurements
        self.tags = updated_info.tags
        self.has_bg_layer = updated_info.has_bg_layer
        self.bg_layer_id = updated_info.bg_layer_id

    def delete_result_layer(self, layer_id):
        layer = self.select_result_layer(layer_id)

        if layer_id == self.bg_layer_id:
            self.set_bg_false()

        layer.delete()

        self.refresh_from_db()

    def calculate_ground_truth_layer(self, layer_id_list, suffix=""):
        '''
        expects a list of layer ids and optionally a suffix.
        Ground Truth is estimated by SimpleITK's STAPLE probabilities.
        For ground truth estimation layer will be binarized, all labels > 0 will be unified and represented as foreground (==1) in returned mask.
        '''
        label_array_list = [crud.read_result_layer_by_uid(
            layer_id).to_int_class().data for layer_id in layer_id_list]
        ground_truth_estimation_array = utils_results.staple_gte(
            label_array_list)
        hint = f"Following Label Layers were used to estimate the ground truth: {layer_id_list}"
        int_result_layer = IntImageResultLayer(
            uid=-1,
            name=f"ground_truth_estimation_{suffix}",
            hint=hint,
            image_id=self.uid,
            layer_type="labels",
            data=ground_truth_estimation_array
        )

        int_result_layer.on_init()
        print(int_result_layer.uid)
        self.refresh_from_db()
        self.measure_mask_in_image(int_result_layer.uid)


class IntExperimentGroup(BaseModel):
    uid: int
    experiment_id: int
    name: str
    hint: str = ""
    description: str = ""
    images: List[IntImage] = []
    result_layer_ids: List[int] = []
    measurement_ids: List[int] = []

    def get_experiment_result(self):
        try:
            db_result = crud.read_result_of_experiment_group_by_id(self.uid)
        except:
            self.calculate_result()
            db_result = crud.read_result_of_experiment_group_by_id(self.uid)

        return db_result.to_int_class()

    def calculate_result(self):
        '''
        This function calculates a result from all associated result layers
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
            image = crud.read_image_by_uid(image_id)
            # Calculate BG
            # returns list of mean intensity per pixel values in order of channels#
            bg_mean_pixel_list = image.calculate_background()
            channel_name_list = image.metadata["custom_channel_names"]
            # Get Colnames
            colnames_features = utils_results.get_feature_colnames(
                channel_name_list)
            colnames_background = [
                f"{c}_mean_background_per_pixel" for c in channel_name_list]

            measurement_reshaped = measurement.reshape(
                (measurement.shape[0], -1), order="C")

            # Here, pandas adds a index column
            measurement_df = pd.DataFrame(
                measurement_reshaped, columns=colnames_features)
            for i, bg_colname in enumerate(colnames_background):
                measurement_df[bg_colname] = bg_mean_pixel_list[i]
            measurement_df["n_z_slices"] = image.data.shape[0]

            measurement_df["image"] = f"{image.uid}_{image.metadata['original_filename']}"
            measurement_df["group"] = f"{self.uid}_{self.name}"
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
            print("No Result found, creating new")

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

        return result_df

    def refresh_from_db(self):
        db_image = self.to_db_class()
        updated_info = db_image.refresh_from_db()

        self.name = updated_info.name
        self.hint = updated_info.hint
        self.description = updated_info.description
        self.images = updated_info.images
        self.result_layer_ids = updated_info.result_layer_ids
        self.measurement_ids = updated_info.measurement_ids

    def on_init(self):
        # should be called on every creation
        if self.uid == -1:
            print("On Init IntExperimentGroup:")
            db_group = self.to_db_class()
            db_group.create_in_db()
            self.uid = db_group.uid

            print(f"New Group created with id {self.uid}")

    def to_db_class(self):
        _images = [image.to_db_class() for image in self.images]
        kwargs = self.dict()
        kwargs["images"] = _images
        return c_db.DbExperimentGroup(**kwargs)

    def add_image_by_uid(self, image_uid):
        db_experiment_group = self.to_db_class()
        int_image = db_experiment_group.add_image_by_uid(image_uid)
        self.images.append(int_image)

    def add_result_layer(self, uid):
        db_experiment_group = self.to_db_class()
        db_experiment_group.add_result_layer(uid)

        self.refresh_from_db()

    def add_measurement(self, uid):
        db_experiment_group = self.to_db_class()
        db_experiment_group.add_measurement(uid)

        self.refresh_from_db()

    def remove_image(self, uid):
        db_experiment_group = self.to_db_class()
        db_experiment_group.remove_image(uid)

        self.refresh_from_db()

    def remove_result_layer(self, uid):
        db_experiment_group = self.to_db_class()
        db_experiment_group.remove_result_layer(uid)

        self.refresh_from_db()

    def remove_measurement(self, uid):
        db_experiment_group = self.to_db_class()
        db_experiment_group.remove_measurement(uid)

        self.refresh_from_db()


class IntExperimentResult(BaseModel):
    uid: int
    name: str = ""
    hint: Optional[str] = ""
    description: Optional[str] = ""
    experiment_group_id: int
    result_type: constr(regex=cfg_classes.result_type_regex)
    data: Any

    def on_init(self):
        # should be called on every creation
        if self.uid == -1:
            print("On Init IntExperimentResult:")
            db_result = self.to_db_class()
            db_result.create_in_db()
            self.uid = db_result.uid

            fsr.save_result_df(self.data, db_result.path)

            print(f"New Result created with id {self.uid}")
            # save data to path

    def to_db_class(self):
        kwargs = self.dict()
        del kwargs["data"]

        return c_db.DbExperimentResult(**kwargs)


class IntExperiment(BaseModel):
    uid: int
    name: str
    hint: str = ""
    description: str = ""
    tags: Set[str] = set()
    experiment_groups: List[IntExperimentGroup] = []

    def on_init(self):
        # should be called on every creation
        if self.uid == -1:
            print("On Init IntExperiment:")
            db_experiment = self.to_db_class()
            db_experiment.create_in_db()
            self.uid = db_experiment.uid

            print(f"New Experiment created with id {self.uid}")

    def to_db_class(self):
        experiment_groups = [experiment_group.to_db_class()
                             for experiment_group in self.experiment_groups]

        kwargs = self.dict()
        kwargs["experiment_groups"] = experiment_groups

        return c_db.DbExperiment(**kwargs)

    def add_experiment_group(self, experiment_group_name, hint="", description=""):
        '''
        Function expects a experiment group name and optionally a hint and a description. 
        Creates IntExperimentGroup, transforms to DbExperimentGroup, creates db entry.
        Finally adds experiment group to IntExperiment
        '''
        experiment_group = IntExperimentGroup(
            uid=-1,
            experiment_id=self.uid,
            name=experiment_group_name,
            hint=hint,
            description=description,
        )

        experiment_group.on_init()

        # db_experiment_group = experiment_group.to_db_class()
        # db_experiment_group.create_in_db()

        self.experiment_groups.append(experiment_group)

    def calculate_results(self):
        '''
        This function calls every experiment_group and calculates the corresponding result object.
        '''
        results_groups = []
        assert len(self.experiment_groups) > 0
        for group in self.experiment_groups:
            results_groups.append(group.calculate_result())

    def export_experiment(self, images: bool, masks: bool, rescaled: bool, xDim: int, yDim: int):
        '''
        Function exports the experiment.

        keyword arguments:
        images -- type: bool, if true experiment images will be exported as .tif
        masks -- type: bool, if true masks will transformed to binary and exported as .tif
        rescaled -- type: bool, if true images and masks will be cropped at given coordinates, max-z-projected and exported as .tif
        xDim -- type: int x dimension of rescaled images
        ydim -- type: int y dimension of rescaled images
        '''
        # Export result df, is always exported
        result_df_list = []
        for group in self.experiment_groups:
            result_df_list.append(group.get_experiment_result().data)

        assert len(result_df_list) > 0
        result_df = result_df_list[0]
        print(result_df)
        if len(result_df_list) > 1:
            for _result_df in result_df_list[1:]:
                # merge(_result_df, how = "outer")
                result_df = result_df.append(_result_df, ignore_index=True)

        utils_paths.create_experiment_export_folder(self.uid, self.name)
        df_export_name = utils_paths.make_experiment_export_df_name(
            self.uid, self.name)
        result_df.to_excel(df_export_name)

        for group in self.experiment_groups:
            utils_paths.create_experiment_group_export_folder(
                group.uid, group.name, self.uid, self.name)
            if images:
                utils_paths.create_images_export_folder(
                    group.uid, group.name, self.uid, self.name, False)
            if masks:
                utils_paths.create_masks_export_folder(
                    group.uid, group.name, self.uid, self.name, False)
            if rescaled:
                utils_paths.create_images_export_folder(
                    group.uid, group.name, self.uid, self.name, True)
                utils_paths.create_masks_export_folder(
                    group.uid, group.name, self.uid, self.name, True)

            for image in group.images:
                if images:
                    path = utils_paths.make_export_array_name(
                        image.uid, image.metadata["original_filename"],
                        False,
                        group.uid, group.name,
                        self.uid, self.name,
                        rescaled=False)
                    utils_export.to_tiff(
                        image_array=image.data,
                        path=path,
                        image_name=image.metadata["original_filename"],
                        channel_names=image.metadata["custom_channel_names"],
                        pixel_type=image.metadata["pixel_type"]
                    )
                if rescaled:
                    path = utils_paths.make_export_array_name(
                        image.uid, image.metadata["original_filename"],
                        False,
                        group.uid, group.name,
                        self.uid, self.name,
                        rescaled=True)
                    image_array_max = image.data.max(axis=0)  # MAX Z PROJECT
                    image_array_max_shape = image_array_max.shape
                    if xDim > image_array_max_shape[1] or yDim > image_array_max_shape[2]:
                        image_array_max_cropped = np.zeros((
                            image_array_max_shape[0],
                            yDim,
                            xDim
                        ))
                        image_array_max_cropped[
                            :image_array_max_shape[0],
                            :image_array_max_shape[1],
                            :image_array_max_shape[2]
                        ] = image_array_max
                    else:
                        image_array_max_cropped = image_array_max[:,
                                                                  :yDim, :xDim]
                    utils_export.to_tiff(
                        image_array=image_array_max_cropped,
                        path=path,
                        image_name=image.metadata["original_filename"],
                        channel_names=image.metadata["custom_channel_names"],
                        pixel_type=image.metadata["pixel_type"])

            for result_layer_id in group.result_layer_ids:
                result_layer = crud.read_result_layer_by_uid(
                    result_layer_id).to_int_class()
                int_image = crud.read_db_image_by_uid(
                    result_layer.image_id).to_int_class()
                mask_array, label_list = utils_transformations.multiclass_mask_to_binary(
                    result_layer.data)
                # Mask array has shape (z,y,x), we add c axis again
                mask_array = mask_array[:, np.newaxis, ...]
                channel_names = [result_layer.name]
                if masks:
                    path = utils_paths.make_export_array_name(
                        int_image.uid, int_image.metadata["original_filename"],
                        True,
                        group.uid, group.name,
                        self.uid, self.name,
                        rescaled=False)

                    utils_export.to_tiff(
                        image_array=mask_array,
                        path=path,
                        image_name=image.metadata["original_filename"],
                        channel_names=channel_names, mask=True)

                if rescaled:
                    path = utils_paths.make_export_array_name(
                        int_image.uid, int_image.metadata["original_filename"],
                        True,
                        group.uid, group.name,
                        self.uid, self.name,
                        rescaled=True)
                    mask_array_max = mask_array.max(axis=0)
                    mask_array_max_shape = mask_array_max.shape
                    if xDim > mask_array_max_shape[1] or yDim > mask_array_max_shape[2]:
                        mask_array_max_cropped = np.zeros((
                            mask_array_max_shape[0],
                            yDim,
                            xDim
                        ))
                        mask_array_max_cropped[
                            :mask_array_max_shape[0],
                            :mask_array_max_shape[1],
                            :mask_array_max_shape[2]
                        ] = mask_array_max
                    else:
                        mask_array_max_cropped = mask_array_max[:,
                                                                :yDim, :xDim]
                    utils_export.to_tiff(
                        image_array=mask_array_max_cropped,
                        path=path,
                        image_name=image.metadata["original_filename"],
                        channel_names=channel_names, mask=True)


class IntClassifier(BaseModel):
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

        path_clf = db_classifier.path_clf
        path_test_train = db_classifier.path_test_train

        if self.clf_type == "rf_segmentation":
            fsr.save_classifier(self.classifier, path_clf)
            fsr.save_classifier_test_train(
                self.test_train_data, path_test_train)

        if self.clf_type == "deepflash_model":
            # We expect self.classifier to be a list of pathlib.Paths
            fsr.save_deepflash_model(self.classifier, path_clf)

    def to_db_class(self):
        kwargs = self.dict()
        del kwargs["classifier"]
        del kwargs["test_train_data"]
        if not self.uid == -1:
            kwargs["path_clf"] = self.classifier

        return c_db.DbClassifier(**kwargs)

    # RF SEGMENTATION METHODS
    def is_multichannel(self):
        if self.clf_type == "rf_segmentation":
            return self.params["multichannel"]
        else:
            print("Multichannel is not an option for clf of type rf_segmentation")
            return False
