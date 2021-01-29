import numpy as np
import skimage.draw
import skimage.measure
import scipy.ndimage
import skimage.feature
import skimage.segmentation
import skimage.morphology


def shapes_to_mask(shapes_layer_data, mask_shape):
    ''' 
    Expects a list of length n of arrays with n being the number of shapes. Arrays have dims (m, 3) for z stacks and ?(m, 2)? for single layer images.
    m is the number of points defining our polygon.
    Limitations: 
        - Only works with polygons restrained to a single z-plane
        - Polygons may not intersect. If polygons intersect, highest label prevails.
    '''
    mask = np.zeros(mask_shape)
    for i, polygon in enumerate(shapes_layer_data):
        try: 
            z_index = int(polygon[0, 0])
            polygon = polygon[:, 1:] # we delete the z dimension because we expect the array to be in a single plane
            poly_mask = skimage.draw.polygon2mask(mask[z_index].shape, polygon)
            mask[z_index] = np.where(poly_mask == True, i+1, mask[z_index])
        except: 
            print("No valid shape, make sure shape layer only consists of polygons!")
    
    return mask

def multiclass_mask_to_binary(mask):
    '''
    Expects mask of shape (z,y,x). 
    Returns binary array and list of unique values before transformation
    '''
    classes = np.unique(mask)
    mask[mask != 0] = 1
    
    return mask, classes

def binary_mask_to_multilabel(mask, watershed = True):
    '''
    Expects a mask of type boolean and shape (z,y,x).
    Returns a multiclass mask and a list of unique labels. Classes are integers for each calculated individual object. 
    '''           
    mask = skimage.measure.label(mask)
    classes = np.unique(mask)
    
    return mask, classes

def watershed(mask, compactness, watershed_line = True):
    image = mask.copy()
    if mask.max() < 2:
        distance = scipy.ndimage.distance_transform_edt(image)
        coords = skimage.feature.peak_local_max(distance, footprint=np.ones((3, 3)), labels=image)
        _mask = np.zeros(distance.shape, dtype=bool)
        _mask[tuple(coords.T)] = True
        markers, _ = scipy.ndimage.label(_mask)
        labels = skimage.segmentation.watershed(-distance, markers, mask=image, watershed_line = watershed_line, compactness = compactness)
        return labels 

    else: 
        print("Watershed function currently only supports binary masks!")

def binary_closing(mask, d):
    selem = np.ones((d,d))
    mask = skimage.morphology.binary_closing(mask, selem)

    return mask

def z_project(image_array, mode = "max"):
    '''
    Expects an image array of shape (z,c,y,x) and a mode.
    Mode must a value of ["max", "min"].
    Returns an array of shape (c,y,x)
    '''
    
    # axis for z projection is 0    
    if mode == "max":
        image_array_projected = image_array.max(axis = 0)
    elif mode == "min":
        image_array_projected = image_array.min(axis = 0)
    else: 
        print(f"{mode} is not a valid mode.\nvalue must be one of: ['max', 'min']")
        print("Defaulting to max z projection")
        image_array_projected = image_array.max(axis = 0)
        
    return image_array_projected