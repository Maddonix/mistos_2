import xtiff

def to_tiff(image_array, path, image_name, channel_names):
    xtiff.to_tiff(
        img = image_array,
        file = path,
        image_name = image_name, 
        channel_names = channel_names
    )
