import napari

def add_layer_from_int_layer(viewer, intImageResultLayer, image_scale, visible):
    _name = intImageResultLayer.name
    _type = intImageResultLayer.layer_type
    _data = intImageResultLayer.data
    
    if _type == "labels":
        viewer.add_labels(_data, name = _name, scale = image_scale, visible = visible)
    elif _type == "points":
        viewer.add_points(_data, name = _name, scale = image_scale, visible = visible)
    elif _type == "shapes":
        viewer.add_shapes(_data, name = _name, scale = image_scale, visible = visible)
             
def make_image_layer(data, name, image_scale = None, rgb = False, blending = "additive", colormap = "Greys"):
    layer = napari.layers.image.Image(data, name = name, rgb = False, scale = image_scale, blending = blending, colormap = colormap)
    return layer


# def save_label_layer_to_file(array):



# ('Diverging', [
#             'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
#             'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
# ('Sequential', [
# 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
# 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
# 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
# ('Sequential (2)', [
# 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
# 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
# 'hot', 'afmhot', 'gist_heat', 'copper']),