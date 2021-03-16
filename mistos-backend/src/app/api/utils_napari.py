import napari
from skimage.measure import regionprops
from vispy.geometry.rect import Rect
import numpy as np
import skimage.morphology as morphology
from app.api import utils_transformations


def add_layer_from_int_layer(viewer, intImageResultLayer, image_scale, visible):
    _name = intImageResultLayer.name
    _type = intImageResultLayer.layer_type
    _data = intImageResultLayer.data

    if _type == "labels":
        viewer.add_labels(_data, name=_name,
                          scale=image_scale, visible=visible)
    elif _type == "points":
        viewer.add_points(_data, name=_name,
                          scale=image_scale, visible=visible)
    elif _type == "shapes":
        viewer.add_shapes(_data, name=_name,
                          scale=image_scale, visible=visible)


def make_image_layer(data, name, image_scale=None, rgb=False, blending="additive", colormap="Greys"):
    layer = napari.layers.image.Image(
        data, name=name, rgb=False, scale=image_scale, blending=blending, colormap=colormap)
    return layer


def get_zoom_view_on_label(layer, image_scale):
    '''
    Expects a binary mask with only the label you want to zoom into and a image_scale tuple (z,y,x). Draws bounding box around label, with 1.5 times the width and heigth of the smallest possible bounding box.
    Returns dictionary suitable to pass to set state of Napari viewer
    '''
    layer = layer.max(axis=0)  # max z project
    _bbox = regionprops(layer)[0].bbox
    _bbox = [_ for _ in _bbox]
    print(f"Bounding Box = {_bbox}")
    _bbox[0] = _bbox[0]*image_scale[-2]
    _bbox[2] = _bbox[2]*image_scale[-2]
    _bbox[1] = _bbox[1]*image_scale[-1]
    _bbox[3] = _bbox[3]*image_scale[-1]

    print(f"Bounding Box after scaling = {_bbox}")

    x = _bbox[1]
    y = _bbox[0]
    w = _bbox[3] - x
    h = _bbox[2] - y
    x = x-1*w
    w = 3 * w
    y = y-1*h
    h = 3 * h
    print(Rect(x, y, w, h))
    return {"rect": Rect(x, y, w, h)}


def _remove_small_objects(segmentation_labels, px: int, conn: int):
    '''
    Method to remove instances with less pixels (grouping by connectivity) than px.
    Returns label array without these instances.

    Parameters:

        - segmentation labels: array of shape z,y,x
        - px: labels smaller than px will be deleted
        - conn: connectivity used

    '''
    shape = segmentation_labels.shape
    if segmentation_labels.max() == 1:
        segmentation_labels = segmentation_labels.astype(bool)
    _segmentation_labels = morphology.remove_small_objects(
        segmentation_labels, px, conn)
    assert shape == segmentation_labels.shape
    return _segmentation_labels


def _remove_small_holes(segmentation_labels, px: int, conn: int):
    shape = segmentation_labels.shape
    if segmentation_labels.max() == 1:
        is_binary = True
    else:
        is_binary = False
    segmentation_labels = morphology.remove_small_holes(
        segmentation_labels, px, conn)
    if is_binary == False:
        segmentation_labels, _classes = utils_transformations.binary_mask_to_multilabel(
            segmentation_labels)
    assert shape == segmentation_labels.shape
    return segmentation_labels
