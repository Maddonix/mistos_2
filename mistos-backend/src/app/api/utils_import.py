import zarr
import javabridge
import bioformats
import numpy as np
import json
import xml
import app.api.classes_internal as c_int
import skimage
import os
from cfg import cfg

#  Start Javabridge for bioformats_importer
javabridge.start_vm(class_path = bioformats.JARS)

def save_zarr(index, array, metadata_dict, metadata_omexml, filepath_zarr, filepath_metadata):
    '''
    Saves Image including Metadata
    '''
    zarr.save_array(filepath_zarr, array)
    metadata_img = metadata_dict["images"][index]
    metadata_img["original_filename"] = metadata_dict["original_filename"]
    with open(filepath_metadata, "w") as file:
        json.dump(metadata_img, file, indent = 3)
        
    metadata_string = metadata_omexml.to_xml(encoding = "utf-8")
    pretty_xml_str = xml.dom.minidom.parseString(metadata_string).toprettyxml(indent = "\t")
    
    with open(filepath_metadata.replace("json", "xml"), "w", encoding = "utf-8") as file:
        file.write(pretty_xml_str)
    
def load_zarr(filepath_zarr, filepath_metadata):
    '''
    Loads Image including Metadata
    '''
    # id will be passed from db in future
    # hint and description will be passed as string or filepath to textfile from db
    img = zarr.convenience.load(filepath_zarr)
    with open(filepath_metadata, "r") as file:
        metadata_dict = json.load(file)
    
    # Make sure we have 4 dimensions
    assert len(img.shape) == 4
    
    return img, metadata_dict

def load_metadata_only(filepath_metadata):
    '''
    loads just an images metadata
    '''
    with open(filepath_metadata, "r") as file:
        metadata_dict = json.load(file)

    return metadata_dict

def save_label_layer_to_zarr(array, filepath):
    '''
    Saves label array to zarr
    '''    
    _shape = array.shape
    if len(_shape) == 2:
        zarr.save_array(filepath, array)
    
    elif len(_shape) == 3:
        zarr.save_array(filepath, array)
        # saving process will probably be the same, but i want to keep this in mind
    
    else:
        print(f"Array with shape {_shape} not valid as label")
        
def load_label_layer_from_zarr(filepath):
    '''
    Loads label layer and returns a label layer object
    '''
    array = zarr.convenience.load(filepath)

    return array

def acquire_image_metadata_dict(metadata_OMEXML, filename):
    n_series = get_number_of_series(metadata_OMEXML)
    
    my_features = {
        "n_series": n_series,
        "original_filename": filename,
        "images": {i: {} for i in range(n_series)}
    }
        
    for i in range(n_series):
        my_features["images"][i]["image_name"] = metadata_OMEXML.image(i).Name
        my_features["images"][i]["image_ID"] = metadata_OMEXML.image(i).ID.replace(":", "_")
        my_features["images"][i]["image_acquisition_date"] = metadata_OMEXML.image(i).AcquisitionDate

        my_features["images"][i]["pixel_dimensions"] = metadata_OMEXML.image(i).Pixels.DimensionOrder
        my_features["images"][i]["pixel_type"] = metadata_OMEXML.image(i).Pixels.PixelType
        my_features["images"][i]["pixel_size_x"] = metadata_OMEXML.image(i).Pixels.SizeX
        my_features["images"][i]["pixel_size_y"] = metadata_OMEXML.image(i).Pixels.SizeY
        my_features["images"][i]["pixel_size_z"] = metadata_OMEXML.image(i).Pixels.SizeZ
        my_features["images"][i]["pixel_size_slices"] = metadata_OMEXML.image(i).Pixels.SizeC
        my_features["images"][i]["pixel_size_physical_x"] = metadata_OMEXML.image(i).Pixels.PhysicalSizeX
        my_features["images"][i]["pixel_size_physical_y"] = metadata_OMEXML.image(i).Pixels.PhysicalSizeY
        my_features["images"][i]["pixel_size_physical_z"] = metadata_OMEXML.image(i).Pixels.PhysicalSizeZ
        my_features["images"][i]["pixel_size_physical_unit_x"] = metadata_OMEXML.image(i).Pixels.PhysicalSizeXUnit
        my_features["images"][i]["pixel_size_physical_unit_y"] = metadata_OMEXML.image(i).Pixels.PhysicalSizeYUnit
        my_features["images"][i]["pixel_size_physical_unit_z"] = metadata_OMEXML.image(i).Pixels.PhysicalSizeZUnit

        my_features["images"][i]["n_channels"] = metadata_OMEXML.image(i).Pixels.channel_count # Returns Number of Channels
        my_features["images"][i]["channel_names"] = [metadata_OMEXML.image(i).Pixels.Channel(n_channel).Name for n_channel in range(my_features["images"][i]["n_channels"])]
        
        my_features["images"][i]["custom_channel_names"] = my_features["images"][i]["channel_names"]
        
        
    return my_features

def get_number_of_series(metadata_OMEXML): 
    '''
    Iterates over images in metadata_omexml. Returns number of images in series.
    '''
    for i in range(9999):
        try:
            metadata_OMEXML.image(i)
        except:
            # print(f"The imported file has {i} image series")
            break
    return i

def read_image_of_series(path, metadata_dict, n_series = 0):
    '''
    Reads image number n of series from path. 
    Intensity values are rescaled to floats between 0 and 1.
    Returns zarr of shape (z,c,y,x) and metadata_dict.
    '''
    tmp_reader_key = "_"
    
    z_dim = metadata_dict["images"][n_series]["pixel_size_z"]
    x_dim = metadata_dict["images"][n_series]["pixel_size_x"]
    y_dim = metadata_dict["images"][n_series]["pixel_size_y"]
    c_dim = metadata_dict["images"][n_series]["n_channels"]
    pixel_size_channels = metadata_dict["images"][n_series]["pixel_size_slices"]
    
    # Set dimensions of z stack
    z_stack = np.zeros((
        z_dim,
        c_dim,
        y_dim,
        x_dim
        ), dtype = float 
    )
    
    for z in range(metadata_dict["images"][n_series]["pixel_size_z"]):
        with bioformats.get_image_reader(tmp_reader_key, path) as reader:

            image = reader.read(series = n_series, z = z, rescale = True)
            dim_order = reader.rdr.getDimensionOrder()
            bioformats.release_image_reader(tmp_reader_key)  
            
        # Special Case: Greyscale Image is read as rgb
        # We transform the "rgb" image to a greyscale image
        if c_dim == 1 and pixel_size_channels == 3:
            image = skimage.color.rgb2gray(image)            

        # Special Case: greyscale image
        # Greyscale images will not have a c dimension, we add it
        if c_dim == 1:
            image = image[:,:, np.newaxis] # Has shape (x,y,c)
            
        image = np.moveaxis(image, -1, 0) # Rearrange to fit our dimension convention (c,y,x)
        
        z_stack[z] = image
    
    return (z_stack, n_series)

def read_image_file(path, n_series = -1, big_file = False):
    '''
    Function expects a filepath to a compatible image file (may be series or single image). Returns list of tuples (zarr, metadata_dict,  original_metadata)
    '''
    # First we read the metadata of our image to see what exactly we are expecting
    # Exit the function if metadata can not be read    
    try:
        metadata_string = bioformats.get_omexml_metadata(path)
        metadata_OMEXML = bioformats.OMEXML(metadata_string)
    except: 
        print(f"Could not read image file at {path}")
        print("Make sure it is a compatible file format!")
        return
    
    filename = path.split("/")[-1]
    # Check file size
    file_size = os.path.getsize(path)/10e5 
    if file_size > cfg["max_file_size_single_import"]:
        big_file = True
        if n_series == -1:
            print(f"warning, big file with size {os.path.getsize(path)/10e5} mb detected!\nIf you import an image series consider importing only single images to prevent crashes.")
    
    # Create metadata dictionary
    metadata_dict = acquire_image_metadata_dict(metadata_OMEXML, filename)
    _n_series = metadata_dict["n_series"]
    
    image_list = []
    if n_series == -1:
        for i in range(_n_series):
            image = read_image_of_series(path, metadata_dict, n_series = i)
            image_list.append(image)
            
    else:
        image = read_image_of_series(path, metadata_dict, n_series = n_series)
        image_list.append(image)
    
    return image_list, metadata_dict, metadata_OMEXML
