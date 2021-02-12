import napari
from PyQt5.QtCore import Qt

from typing import List
from magicgui import magicgui
import skimage.filters as filters
import skimage.morphology as morphology
from stardist import random_label_cmap
from stardist.models import StarDist2D
import numpy as np

from app import crud
from app.api import utils_napari
from app.api import utils_import
from app.api import classes_internal as c_int
from app.api import utils_segmentation_random_forest as utils_seg_rf
from app.api import utils_transformations


lbl_cmap = random_label_cmap()

def view(intImage: c_int.IntImage, display_bg_layer = False, display_segmentation_layers = False, intImageResultLayerList: List[c_int.IntImageResultLayer] = None):   
    '''
    Expects image array, metadata dict and list of additional layer tuples (array, layer_type)
    '''  

    intImageResultLayerList = []

    image = intImage.data
    metadata = intImage.metadata
    image_scale = intImage.get_image_scaling()
    channel_names = intImage.metadata["channel_names"]
    n_channels = metadata["pixel_size_slices"]
    __ACTIVE_LAYER__ = None
    rf_classifiers = intImage.get_classifiers("rf_segmentation")

    if len(channel_names) != image.shape[1]: # axis 1 is channel axis
        channel_names = None
    
    # if display_bg_layer == True:
    #     pass 
    #     # Currently not needed as bg_layer is part of segmentation layers 
    #     # intImageResultLayerList.append(self.bg_layer)

    if display_segmentation_layers == True:
        intImageResultLayerList.extend(intImage.image_result_layers)

    with napari.gui_qt():
        viewer = napari.Viewer(title = f"{intImage.name}", show = True)       
        viewer.add_image(image.data, channel_axis = 1, scale = image_scale, name = channel_names) 
        
        if intImageResultLayerList:
            for layer in intImageResultLayerList:
                print("add layers")
                print(layer)
                utils_napari.add_layer_from_int_layer(viewer, layer, image_scale = image_scale, visible = False)
            
        @magicgui(
                    call_button = "Nuclei Segmentation",
                )
        def apply_stardist(): # -> napari.types.LabelsData: #With this syntax we could directly return the layer to the viewer. Since we need to scale it first, this doesn't work
            """Apply StarDist2D Nuclei Segmentation"""
            layer = viewer.active_layer
            mode = "max_z"

            if layer:
                # Max Z Projection
                if mode == "max_z":
                    # Load Model
                    model = StarDist2D.from_pretrained("2D_versatile_fluo")
                    # Max Z
                    layer_max = layer.data.max(axis = 0)
                    # Normalize
                    layer_max = layer_max/layer_max.max()
                    _labels, details = model.predict_instances(layer_max)
                    
                    # make z stack mask
                    labels = np.zeros(layer.data.shape)
                    labels[:] = _labels

                # 3 D Segmentation    
                elif mode == "3D":
                    pass
                    # # TO DO: Load 3 D model
                    # labels = np.zeros(layer.data.shape)
                    # # Iterate over every z-slice and predict
                    # for n in range(layer.data.shape[0]):
                    #     _slice = layer.data[n]
                    #     # Normalize
                    #     _slice = _slice/_slice.max()
                    #     _labels, details = model.predict_instances(_slice)
                    #     labels[n] = _labels
                
                print(labels.shape)
                viewer.add_labels(labels, name = "StarDistNuclei", scale = image_scale, visible = True)

        @magicgui(call_button = "Save Label")
        def save_label_layer():
            """
            Save selected layer to file and db.
            Refresh image from db, now has new layer in layerlist
            now measure layer
            """
            layer = viewer.active_layer

            if layer:
                print(f"Saving Layer with shape {layer.data.shape} for image with shape {intImage.data.shape}")
                new_label_layer = c_int.IntImageResultLayer(
                    uid = -1,
                    name = layer.name,
                    image_id = intImage.uid,
                    layer_type = "labels",
                    data = layer.data
                )

                new_label_layer.on_init()
                intImage.refresh_from_db()
                # measure layer
                measurement = intImage.measure_mask_in_image(new_label_layer.uid, subtract_background=False)
                print("napari viewer save label layer")
                print(measurement)
                refresh()

               
        @magicgui(call_button = "Save BG Layer")
        def save_background_layer():
            layer = viewer.active_layer
            
            if intImage.has_bg_layer == True:
                print("Image already has a background layer")
                return
            print(f"Saving BG Layer with shape {layer.data.shape} for image with shape {intImage.data.shape}")
            if layer:
                new_bg_layer = c_int.IntImageResultLayer(
                    uid = -1,
                    name = layer.name,
                    image_id = intImage.uid,
                    layer_type = "labels",
                    data = layer.data
                )
                new_bg_layer.on_init()
                intImage.set_bg_true(new_bg_layer)

                refresh()
        
        @magicgui(
                    call_button = "Segmentation",
                    multichannel={"choices": [True, False]},
                    tags = {"widget_type": "LineEdit", "label": "tags"},
                    layout = "vertical"
                )
        def semiautomatic_segmentation_random_forest(
            layer_image: napari.layers.Image, 
            layer_labels: napari.layers.Labels,
            tags: str,
            multichannel = False,
            ):
                        
            img_array = layer_image.data
            label_array = layer_labels.data
            assert img_array.shape == label_array.shape
            
            if multichannel:
                # get all original image layers
                img_array = image.data # shape: (z,c,y,x)
                # for multichannel segmentation we expect c to be the last dimension
                img_array = np.moveaxis(img_array, 1, -1)
                
            # if we have only one z slice, we tranform the image to shape (y,x)
            if img_array.shape[0] == 1:
                img_array = img_array[0,...]
                label_array = label_array[0,...]
            
            segmentation_labels, clf = utils_seg_rf.semi_automatic_classification(img_array, label_array, multichannel = multichannel)

            classifier = c_int.IntClassifier(
                uid = -1,
                name = f"random_forest_on_{intImage.name}",
                classifier = clf,
                clf_type = "rf_segmentation",
                test_train_data = [(intImage.data, label_array)],
                params = {
                    "multichannel": multichannel
                }, 
                tags = set(tags.split(";"))
            )
            classifier.on_init()

            # will only be a binary mask if we have marked only labels 1==background, 2==regions of interest

            viewer.add_labels(segmentation_labels, name = "Segmentation", scale = image_scale)

        @magicgui(call_button = "To individuals")
        def binary_mask_to_multilabel():
            layer = viewer.active_layer

            segmentation_labels = layer.data
            segmentation_labels, _classes = utils_transformations.binary_mask_to_multilabel(segmentation_labels)
            layer.data = segmentation_labels

        @magicgui(call_button = "del small obj", px={"widget_type": "SpinBox", "max": 1000, "min": 1}, conn = {"widget_type": "SpinBox", "max":50, "min": 1},
        layout = "vertical")
        def remove_small_objects(px:int, conn:int):
            layer = viewer.active_layer

            segmentation_labels = layer.data
            if segmentation_labels.max() == 1:
                segmentation_labels = segmentation_labels.astype(bool)

            segmentation_labels = morphology.remove_small_objects(segmentation_labels,px,conn)
            layer.data = segmentation_labels

        @magicgui(call_button = "del small holes", px={"widget_type": "SpinBox", "max": 1000, "min": 1, "value": 50}, conn = {"widget_type": "SpinBox", "max":50, "min": 1, "value": 5},
        layout = "vertical")
        def remove_small_holes(px:int, conn:int):
            layer = viewer.active_layer

            segmentation_labels = layer.data
            segmentation_labels = morphology.remove_small_holes(segmentation_labels,px,conn)
            layer.data = segmentation_labels

        @magicgui(call_button = "Watershed", compactness={"widget_type": "FloatSpinBox", "max": 50, "min": 0, "value":5}, layout = "vertical")
        def watershed(compactness: float):
            layer = viewer.active_layer
            labels = utils_transformations.watershed(layer.data,compactness, watershed_line=True)
            viewer.active_layer.data = labels

        @magicgui(call_button = "Area Closing", selem_edge_len = {"widget_type": "SpinBox", "max": 50, "min": 1, "value": 10}, layout = "vertical")
        def area_closing(selem_edge_len):
            layer = viewer.active_layer

            mask = utils_transformations.binary_closing(layer.data, selem_edge_len)
            layer.data = mask

        @magicgui(call_button = "Refresh Image")
        def refresh():
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

            viewer.add_image(intImage.data, channel_axis = 1, scale = image_scale, name = channel_names) 

            intImageResultLayerList = []

            # if display_bg_layer == True:
            #     pass 
            #     # intImageResultLayerList.append(self.bg_layer)

            if display_segmentation_layers == True:
                intImageResultLayerList.extend(intImage.image_result_layers)

            if intImageResultLayerList:
                for layer in intImageResultLayerList:
                    utils_napari.add_layer_from_int_layer(viewer, layer, image_scale = image_scale, visible = False)

        @magicgui(
            call_button = "Load&Segment",
            classifier = {"choices": [clf_name for clf_name in list(rf_classifiers.keys())]},
            threshold = {"widget_type": "SpinBox", "min": 0, "max": 100, "value": 50},
            layout = "vertical"
        )
        def load_clf_and_apply(classifier, threshold):
            clf_uid = rf_classifiers[classifier]
            int_clf = crud.read_classifier_by_uid(clf_uid)
            multichannel = int_clf.is_multichannel()
            threshold = threshold/100

            image_array = viewer.active_layer.data
            # if z-dim == 1, reduce dimensionality
            if image_array.shape[0] == 1:
                image_array = image_array[0,...]

            if multichannel == True:
                print("multilabel not yet supported")
            else: 
                image_features = utils_seg_rf.multiscale_basic_features(image_array, multichannel = multichannel)
                prediction = utils_seg_rf.predict_proba_segmenter(image_features, int_clf.classifier, threshold)

                kwargs = {
                    "uid": -1,
                    "name": f"rf_{classifier}_segmentation",
                    "hint": "",
                    "image_id": intImage.uid,
                    "layer_type": "labels",
                    "data": prediction
                    }

                prediction_layer = c_int.IntImageResultLayer(**kwargs)
                utils_napari.add_layer_from_int_layer(viewer = viewer, intImageResultLayer = prediction_layer, image_scale = image_scale, visible = True)

        # Shortcuts
        # print active layer
        # @viewer.bind_key('p')
        # def print_active_layer(viewer):
        #     print("P pressed")
        #     print(viewer.active_layer)

        # Build UI
        # Top
        viewer.window.add_dock_widget(save_label_layer, area = "top")
        viewer.layers.events.changed.connect(save_label_layer.reset_choices)

        viewer.window.add_dock_widget(save_background_layer, area = "top")
        viewer.layers.events.changed.connect(save_background_layer.reset_choices)
       
        viewer.window.add_dock_widget(load_clf_and_apply, area = "top")
        viewer.layers.events.changed.connect(load_clf_and_apply.reset_choices)

        viewer.window.add_dock_widget(refresh, area = "top")

        # Left
        viewer.window.add_dock_widget(semiautomatic_segmentation_random_forest, area = "left")
        viewer.layers.events.changed.connect(semiautomatic_segmentation_random_forest.reset_choices)

        # Bottom
        viewer.window.add_dock_widget(remove_small_objects, area = "bottom")

        viewer.window.add_dock_widget(remove_small_holes, area = "bottom")

        viewer.window.add_dock_widget(area_closing, area = "bottom")

        viewer.window.add_dock_widget(watershed, area = "bottom")

        viewer.window.add_dock_widget(binary_mask_to_multilabel, area = "bottom")
        
        viewer.window.add_dock_widget(apply_stardist, area = "bottom")
        
        
########### REMOVED FUNCTIONS
        # @magicgui(call_button = "Delete Label")
        # def delete_label_layer():
        #     '''
        #     This function deletes a layer from the database, the fileserver, but not from the image itself. 
        #     If you delete a layer as a mistake, you can simply choose it in the napari viewer and add it again via "save_label_layer"
        #     '''
        #     layer = viewer.active_layer

        #     layer_name = layer.name
        #     layer_names = [_layer.name for _layer in intImageResultLayerList]

        #     if layer_name in layer_names:
        #         index = layer_names.index(layer_name)
        #     else:
        #         print("Layer not in Layerlist. Either the image does not exist in db or you renamed it within the viewer. Renaming within the viewer is not fully supported yet")
        #         return

        #     int_result_layer = intImageResultLayerList[index]
        #     _layer_id = int_result_layer.uid
        #     intImage.delete_result_layer(_layer_id)

        #     refresh()



        # viewer.window.add_dock_widget(delete_label_layer, area = "top")
        # viewer.layers.events.changed.connect(delete_label_layer.reset_choices)