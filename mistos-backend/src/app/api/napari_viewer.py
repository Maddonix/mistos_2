# pylint:disable=no-name-in-module, import-error, no-member
from magicgui.types import ChoicesCallback
import napari
from napari.layers.labels import Labels
import warnings

import pathlib
from typing import List
from magicgui import magicgui
from magicgui.widgets import SpinBox, FileEdit, CheckBox, Container, PushButton, ComboBox
import skimage.filters as filters
import skimage.morphology as morphology
from skimage import img_as_ubyte, img_as_bool, img_as_uint
from skimage.morphology import binary_dilation, binary_erosion
from stardist import random_label_cmap
from stardist.models import StarDist2D, StarDist3D
import numpy as np
import os

from app import crud
from app.api import utils_napari
from app.api import classes
from app.api import utils_segmentation_random_forest as utils_seg_rf
from app.api import utils_transformations


# Activate experimental napari features: async and octree
os.environ["NAPARI_OCTREE"] = "1"
os.environ["NAPARI_ASYNC"] = "1"

lbl_cmap = random_label_cmap()


def view(
        intImage: classes.IntImage,
        display_segmentation_layers=False,
        intImageResultLayerList: List[classes.IntImageResultLayer] = None):
    '''
    Expects image array, metadata dict and list of additional layer tuples (array, layer_type)
    '''
    intImageResultLayerList = []
    image = intImage.data
    metadata = intImage.metadata
    image_scale = intImage.get_image_scaling()
    channel_names = intImage.metadata["channel_names"]
    __ACTIVE_LAYER__ = None
    rf_classifiers = intImage.get_classifiers("rf_segmentation")

    if len(channel_names) != image.shape[1]:  # axis 1 is channel axis
        channel_names = None

    if display_segmentation_layers == True:
        intImageResultLayerList.extend(intImage.image_result_layers)

    with napari.gui_qt():
        viewer = napari.Viewer(title=f"{intImage.name}", show=True)
        viewer.add_image(image.data, channel_axis=1,
                         scale=image_scale, name=channel_names)

        if intImageResultLayerList:
            for layer in intImageResultLayerList:
                print("add layers")
                print(layer)
                utils_napari.add_layer_from_int_layer(
                    viewer, layer, image_scale=image_scale, visible=False)

        # -> napari.types.LabelsData: #With this syntax we could directly return the layer to the viewer. Since we need to scale it first, this doesn't work
        def apply_stardist(event=None):
            """
            Apply StarDist2D Nuclei Segmentation
            """
            print("ASD")
            layer = viewer.active_layer
            # Max Z Projection
            # Load Model
            model = StarDist2D.from_pretrained("2D_versatile_fluo")
            # Max Z
            layer_max = layer.data.max(axis=0)
            # Normalize
            layer_max = layer_max/layer_max.max()
            _labels, details = model.predict_instances(layer_max)
            # make z stack mask
            labels = np.zeros(layer.data.shape, dtype=int)
            labels[:] = _labels
            viewer.add_labels(labels, name="StarDistNuclei",
                              scale=image_scale, visible=True)

        def apply_stardist_3d(event=None):
            model_path = pathlib.Path(
                r"D:\Programming\github\model_zoo\model_stardist\3D_Iso_Basic")
            # 3 D Segmentation
            layer = viewer.active_layer
            model = StarDist3D(name="stardist3d",
                               basedir=model_path.as_posix())
            _labels, details = model.predict_instances(layer.data)
            viewer.add_labels(_labels, name="StarDistNuclei3D",
                              scale=image_scale, visible=True)

        def save_label_layer(event=None):
            """
            Save selected layer to file and db.
            Refresh image from db, now has new layer in layerlist
            now measure layer
            """
            layer = viewer.active_layer

            if layer:
                # Get maximum layer amount to set layers datatype
                n_labels = layer.data.max()
                if n_labels == 1:
                    label_array = img_as_bool(layer.data)
                elif n_labels <= 255:
                    label_array = img_as_ubyte(layer.data)
                else:
                    label_array = img_as_uint(layer.data)

                new_label_layer = classes.IntImageResultLayer(
                    uid=-1,
                    name=layer.name,
                    image_id=intImage.uid,
                    layer_type="labels",
                    data=label_array
                )

                new_label_layer.on_init()
                intImage.refresh_from_db()
                # measure layer
                intImage.measure_mask_in_image(
                    new_label_layer.uid)
                refresh()

        def delete_label_layer(event=None):
            '''
            This function deletes a layer from the database, the fileserver, but not from the image itself.
            If you delete a layer as a mistake, you can simply choose it in the napari viewer and add it again via "save_label_layer"
            '''
            print("delete layer called")
            print(checkbox_delete.value)
            confirmed = checkbox_delete.value
            if confirmed:
                layer = viewer.active_layer
                assert type(layer) == Labels
                _layer_id = int(combobox_select_layer.value.split("_")[0])
                print(f"delete layer with id {_layer_id}")
                intImage.delete_result_layer(_layer_id)

                refresh()

        def save_background_layer(event=None):
            '''
            Function to save the currently selected layer as background layer. If a background layer already exists, the layer will not be saved.
            '''
            layer = viewer.active_layer

            if intImage.has_bg_layer == True:
                print("Image already has a background layer")
            else:
                print(
                    f"Saving BG Layer with shape {layer.data.shape} for image with shape {intImage.data.shape}")
                if layer:
                    new_bg_layer = classes.IntImageResultLayer(
                        uid=-1,
                        name="Background",
                        image_id=intImage.uid,
                        layer_type="labels",
                        data=layer.data
                    )
                    new_bg_layer.on_init()
                    intImage.set_bg_true(new_bg_layer)

                    refresh()
        
        
        @magicgui(
            call_button="Segmentation",
            layout="vertical"
        )
        def semiautomatic_segmentation_random_forest(
            layer_labels: napari.layers.Labels
        ):

            label_array = viewer.active_layer.data
            img_array = intImage.data
            # We expect c to be the last dimension
            img_array = np.moveaxis(img_array, 1, -1)

            # if we have only one z slice, we tranform the image to shape (y,x)
            if img_array.shape[0] == 1:
                img_array = img_array[0, ...]
                label_array = label_array[0, ...]

            segmentation_labels, clf = utils_seg_rf.semi_automatic_classification(
                img_array, label_array)

            # classifier = classes.IntClassifier(
            #     uid=-1,
            #     name=f"random_forest_on_{intImage.name}",
            #     classifier=clf,
            #     clf_type="rf_segmentation",
            #     test_train_data=[(intImage.data, label_array)],
            #     metrics={},
            #     params={
            #         "multichannel": multichannel
            #     },
            #     tags=set(tags.split(";"))
            # )
            # classifier.on_init()

            # will only be a binary mask if we have marked only labels 1==background, 2==regions of interest

            viewer.add_labels(segmentation_labels,
                              name="Segmentation", scale=image_scale)
        
        
        def binary_mask_to_multilabel(event=None):
            layer = viewer.active_layer
            assert type(layer) == Labels
            viewer.active_layer.data = utils_transformations.binary_mask_to_multilabel(
                layer.data)[0]

        def remove_small_objects(event=None, px=None, conn=None):
            if px == None:
                px = spin_box_pixels.value
            if conn == None:
                conn = spin_box_conn.value
            layer = viewer.active_layer
            assert type(layer) == Labels
            segmentation_labels = utils_napari._remove_small_objects(
                layer.data, px, conn)
            viewer.active_layer.data = segmentation_labels

        def multiclass_mask_to_binary(event=None):
            layer = viewer.active_layer
            assert type(layer) == Labels
            layer.data = utils_transformations.multiclass_mask_to_binary(
                layer.data)[0]

        def remove_small_holes(event=None, px=None, conn=None):
            if px == None:
                px = spin_box_pixels.value
            if conn == None:
                conn = spin_box_conn.value
            layer = viewer.active_layer
            assert type(layer) == Labels
            viewer.active_layer.data = utils_napari._remove_small_holes(
                layer.data, px, conn)

        def refresh(event=None):
            '''
            The refresh function refreshes
                - the image from database (loads everything but image data again)
                - the classifier list
            Then, all layers are popped from the viewer
            Then, image data data is added as image
            Then, intImageResultLayers are appended
            '''
            intImage.refresh_from_db()
            rf_classifiers = intImage.get_classifiers("rf_segmentation")
            for index in range(len(viewer.layers)):
                viewer.layers.pop(0)
            viewer.add_image(intImage.data, channel_axis=1,
                             scale=image_scale, name=channel_names)
            intImageResultLayerList = []
            if display_segmentation_layers == True:
                intImageResultLayerList.extend(intImage.image_result_layers)
            if intImageResultLayerList:
                for layer in intImageResultLayerList:
                    utils_napari.add_layer_from_int_layer(
                        viewer, layer, image_scale=image_scale, visible=False)
            combobox_select_layer.choices = get_layer_choices()

        # Shortcuts
        # print active layer

        @viewer.bind_key('p')
        def print_active_layer(viewer):
            print("P pressed")
            print(viewer.active_layer)

        @viewer.bind_key('Control-n')
        def zoom_on_next_label(viewer):
            is_label_layer = type(
                viewer.active_layer) == napari.layers.labels.labels.Labels
            if viewer.active_layer and is_label_layer:
                # Make sure we have a panzoomcamera
                assert str(type(viewer.window.qt_viewer.view.camera)
                           ) == "<class 'vispy.scene.cameras.panzoom.PanZoomCamera'>"
                viewer.active_layer.selected_label += 1
                layer = np.where(viewer.active_layer.data ==
                                 viewer.active_layer.selected_label, 1, 0)
                _zoom_view = utils_napari.get_zoom_view_on_label(
                    layer, image_scale)
                viewer.window.qt_viewer.view.camera.set_state(_zoom_view)
                print(image_scale)

        @viewer.bind_key('Control-b')
        def zoom_on_previous_label(viewer):
            is_label_layer = type(
                viewer.active_layer) == napari.layers.labels.labels.Labels

            if viewer.active_layer and is_label_layer:
                # Make sure we have a panzoomcamera
                assert str(type(viewer.window.qt_viewer.view.camera)
                           ) == "<class 'vispy.scene.cameras.panzoom.PanZoomCamera'>"
                viewer.active_layer.selected_label -= 1
                layer = np.where(viewer.active_layer.data ==
                                 viewer.active_layer.selected_label, 1, 0)
                _zoom_view = utils_napari.get_zoom_view_on_label(
                    layer, image_scale)
                viewer.window.qt_viewer.view.camera.set_state(_zoom_view)

        @viewer.bind_key('Control-d')
        def delete_label(viewer):
            active_layer = viewer.active_layer.selected_label
            viewer.active_layer.data = np.where(
                viewer.active_layer.data == active_layer, 0, viewer.active_layer.data)

        @viewer.bind_key('Control-e')
        def expand_label(viewer):
            active_layer = viewer.active_layer
            if active_layer:
                labels = active_layer.data
                active_label = viewer.active_layer.selected_label
                _labels = np.where(labels == active_label, 1, 0)
                for z in range(labels.shape[0]):
                    _labels[z, ...] = binary_dilation(_labels[z, ...])
                labels = np.where(_labels == 1, active_label, labels)
                viewer.active_layer.data = labels

        @viewer.bind_key('Control-r')
        def shrink_label(viewer):
            active_layer = viewer.active_layer
            if active_layer:
                labels = active_layer.data
                active_label = viewer.active_layer.selected_label
                _labels = np.where(labels == active_label, 1, 0)
                for z in range(labels.shape[0]):
                    _labels[z, ...] = binary_erosion(_labels[z, ...])
                labels = np.where(labels == active_label, 0, labels)
                labels = np.where(_labels == 1, active_label, labels)
                viewer.active_layer.data = labels

        # make some widgets

        def get_layer_choices(event=None):
            return [f"{label_layer.uid}_{label_layer.name}" for label_layer in intImage.image_result_layers]

        def on_file_select(event):

            path = pathlib.Path(event.value.value)
            print(path)
            assert path.exists()
            suffix = path.suffix
            supported_roi_formats = [".roi", ".zip"]
            supported_image_formats = [".tif", ".tiff", ".png"]
            if suffix in supported_roi_formats:
                intImage.add_layer_from_roi(path)
                refresh()
            elif suffix in supported_image_formats:
                intImage.add_layer_from_mask(path)
                refresh()
            else:
                warnings.warn(
                    f"{suffix} not part of tested roi or image formats! \n images: {supported_image_formats}\n rois: {supported_roi_formats}")

        file_picker_add_layer = FileEdit(value='upload mask', mode="r")
        file_picker_add_layer.changed.connect(on_file_select)

        button_refresh = PushButton(
            text="Refresh", visible=True, enabled=True)
        button_refresh.changed.connect(refresh)

        button_save_bg = PushButton(
            text="Save Layer as Background", visible=True, enabled=True)
        button_save_bg.changed.connect(save_background_layer)

        button_save_layer = PushButton(
            text="Save Layer", visible=True, enabled=True)
        button_save_layer.changed.connect(save_label_layer)

        combobox_select_layer = ComboBox(
            name="Layer:",
            choices=get_layer_choices(),
            visible=True
        )
        button_delete_layer = PushButton(
            text="Delete Layer", visible=True, enabled=True)
        button_delete_layer.changed.connect(delete_label_layer)
        checkbox_delete = CheckBox(visible=True)

        button_bin_to_multi = PushButton(
            text="To Indiviuals", visible=True, enabled=True)
        button_bin_to_multi.changed.connect(binary_mask_to_multilabel)

        button_multi_to_bin = PushButton(
            text="To Binary", visible=True, enabled=True)
        button_multi_to_bin.changed.connect(multiclass_mask_to_binary)

        button_star_dist = PushButton(
            text="Start StarDist", visible=True, enabled=True)
        button_star_dist.changed.connect(apply_stardist)
        button_star_dist_3d = PushButton(
            text="Start StarDist 3D", visible=True, enabled=True)
        button_star_dist_3d.changed.connect(apply_stardist_3d)

        spin_box_pixels = SpinBox(
            value=1, name='px', label='pixel number:', max=1000)
        spin_box_conn = SpinBox(
            value=1, name='conn', label='connectivety:', max=50)

        button_remove_small_objects = PushButton(
            text="Remove Small Objects", visible=True, enabled=True)
        button_remove_small_objects.changed.connect(remove_small_objects)

        button_remove_small_holes = PushButton(
            text="Remove Small Holes", visible=True, enabled=True)
        button_remove_small_objects.changed.connect(remove_small_holes)

        container_delete_layer = Container(layout="horizontal", widgets=[
            button_delete_layer,
            checkbox_delete
        ])
        container_save_delete = Container(layout="vertical", widgets=[
            button_refresh,
            button_save_bg,
            button_save_layer,
            combobox_select_layer,
            container_delete_layer,
            file_picker_add_layer,
        ])
        container_segmentation = Container(layout="vertical", widgets=[
            button_multi_to_bin,
            button_bin_to_multi,
            button_star_dist,
            button_star_dist_3d,
        ])
        container_utils = Container(layout="vertical", widgets=[
            spin_box_pixels,
            spin_box_conn,
            button_remove_small_objects,
            button_remove_small_holes,
        ])

        container_toolbar = Container(layout="vertical",
                                      widgets=[
                                          container_save_delete,
                                          container_segmentation,
                                          container_utils
                                      ])
        # container_toolbar.show()
        viewer.window.add_dock_widget(container_toolbar, area="right")
        viewer.window.add_dock_widget(semiautomatic_segmentation_random_forest, area = "right")

 # Depreceated for now, as it doesnt work nicely
        # @magicgui(call_button="Watershed", compactness={"widget_type": "FloatSpinBox", "max": 50, "min": 0, "value": 5}, layout="vertical")
        # def watershed(compactness: float):
        #     layer = viewer.active_layer
        #     labels = utils_transformations.watershed(
        #         layer.data, compactness, watershed_line=True)
        #     viewer.active_layer.data = labels

        # @magicgui(call_button="Area Closing", selem_edge_len={"widget_type": "SpinBox", "max": 50, "min": 1, "value": 10}, layout="vertical")
        # def area_closing(selem_edge_len):
        #     layer = viewer.active_layer

        #     mask = utils_transformations.binary_closing(
        #         layer.data, selem_edge_len)
        #     layer.data = mask

        # @magicgui(
        #     call_button="Load&Segment",
        #     # list(rf_classifiers.keys())
        #     classifier={"choices": [clf_name for clf_name in rf_classifiers]},
        #     threshold={"widget_type": "SpinBox",
        #                "min": 0, "max": 100, "value": 50},
        #     layout="vertical"
        # )
        # def load_clf_and_apply(classifier, threshold):
        #     if classifier == "No Classifiers Trained":
        #         print("Train a classifier first!")
        #         return
        #     clf_uid = rf_classifiers[classifier]
        #     int_clf = crud.read_classifier_by_uid(clf_uid)
        #     multichannel = int_clf.is_multichannel()
        #     threshold = threshold/100

        #     image_array = viewer.active_layer.data
        #     # if z-dim == 1, reduce dimensionality
        #     if image_array.shape[0] == 1:
        #         image_array = image_array[0, ...]

        #     if multichannel == True:
        #         print("multilabel not yet supported")
        #     else:
        #         image_features = utils_seg_rf.multiscale_basic_features(
        #             image_array, multichannel=multichannel)
        #         prediction = utils_seg_rf.predict_proba_segmenter(
        #             image_features, int_clf.classifier, threshold)

        #         kwargs = {
        #             "uid": -1,
        #             "name": f"rf_{classifier}_segmentation",
        #             "hint": "",
        #             "image_id": intImage.uid,
        #             "layer_type": "labels",
        #             "data": prediction
        #         }

        #         prediction_layer = classes.IntImageResultLayer(**kwargs)
        #         utils_napari.add_layer_from_int_layer(
        #             viewer=viewer, intImageResultLayer=prediction_layer, image_scale=image_scale, visible=True)