"""
This module provides the main conversion methods.
"""

import os
import sys
import PIL.Image

import camorph
import crucial_property as cp
from model import Camera
import visualizer as vis




def read_cameras(format: str, *args, **kwargs) -> list[Camera]:
    """
    Read the cameras of format `format`

    :param src: The source camera format. Currently possible: COLMAP, fbx, meshroom, unity, mpeg_omaf
    :type src: str
    :param args: The source path. The number of source path arguments is defined by :meth:`model.FileHandler.FileHandler.file_number`
    :return: A list of cameras in the camorph coordinate system convention defined in :class:`model.Camera.Camera`
    :rtype: list[:class:`model.Camera.Camera`]
    """
    src_inst = camorph.imported_instances[format.lower()]
    cams = src_inst.read_file(*args, **kwargs)
    return cams

def write_cameras(format, path, cams, crop=None, scale=None, imdir=None, check_images=False, file_type=None) -> None:
    """
    Write cameras of format `dest` to dest_path

    :param format: The dest camera format. Currently possible: COLMAP, fbx, meshroom, unity, mpeg_omaf
    :param path: The path where to write the cameras
    :param cams: The list of :class:`model.Camera.Camera` to write
    :param crop: A list of type [[x1,y1],[x2,y2]] which specifies the pixel location of the cropping to be applied
    :param scale: A float which represents the relative scale applied in range
    :param imdir: A string to replace the basepath of the current images
    :param file_type: An optional parameter if there are multiple file types (for example, COLMAP has bin and txt)
    :return: None
    """

    splitpath = path.split(os.path.sep)

    # please dont try to supply folders with a dot in the name
    isfile = '.' in splitpath[-1]
    if isfile:
        folder = (os.path.sep).join(splitpath[:-1])
    else:
        folder = path
    if not os.path.isdir(folder):
        os.mkdir(folder)

    dest_inst = camorph.imported_instances[format.lower()]

    # check for crucial properties of output format
    cp.pip_check_properties(dest_inst, cams, camorph.crucial_property_config, path)

    if imdir is not None:
        for cam in cams:
            basename = os.path.basename(cam.source_image)
            cam.source_image = os.path.join(imdir, basename)

    def is_none_or_empty(x):
        if x is None:
            return True
        elif isinstance(x,list):
            return all([i == 0 for i in x])
        else:
            return x == 0

    # recalculate camera parameters for cropped images
    if crop is not None:
        print('cropping intrinsics...')
        # raise exception when distortion is not None or 0
        if type(crop) is not list or type(crop[0]) is not list or type(crop[1]) is not list:
            raise TypeError("Please supply a crop in the format [[x1,y1],[x2,y2]]")
        if crop[0][0] > crop[1][0] or crop[0][1] > crop[1][1]:
            raise ValueError("First crop point must be the upper right, the second must be lower left")
        n_imsize = [crop[1][0] - crop[0][0],crop[1][1]-crop[0][1]]
        for cam in cams:
            if not is_none_or_empty(cam.radial_distortion) or not is_none_or_empty(cam.tangential_distortion):
                raise ValueError("Images cannot be resized if the camera has radial or tangential distortion")
            cam.principal_point = [cam.principal_point[0] - crop[0][0], cam.principal_point[1] - crop[0][1]]
            cam.resolution = n_imsize
            cam.focal_length_mm = cam._focal_length_mm_1()
            cam.fov = cam._fov()
            cam.lens_shift = cam._lens_shift()

    # recalculate camera parameters for scaled images
    if scale is not None:
        print('scaling intrinsics...')
        if type(scale) is not float:
            raise TypeError("Please provide scale as a float")
        for cam in cams:
            cam.resolution = [int(x * scale) for x in cam.resolution]
            cam.principal_point = [x * scale for x in cam.principal_point]
            cam.focal_length_px = cam._focal_length_px()
        check_images = True

    # sanity check for images
    if check_images:
        print('checking images...')
        for cam in cams:
            im = PIL.Image.open(cam.source_image)
            if not (im.height == cam.resolution[0] and im.width == cam.resolution[1]) and not (im.height == cam.resolution[1] and im.width == cam.resolution[0]):
                raise ValueError(f"Resolution of image and intrinsics does not match: image {im.height}x{im.width}, intrinsic {cam.resolution[0]}x{cam.resolution[1]}")

    dest_inst.write_file(cams, path, file_type)

def write_crucial_config_template(cams, path):
    """
    This function writes a template config.json to the desired path

    :param cams: The list of :class:`model.Camera.Camera`
    :param path: The path where to write the config
    :return: None
    """
    cp.write_crucial_config_template(cams, path)

def visualize(cams):
    """
    Visualizes the list of :class:`model.Camera.Camera` with matplotlib
    See :mod:`vis.Visualizer`

    :param cams: The list of :class:`model.Camera.Camera` to visualize
    :return: None
    """
    vis.visualize(cams)

def set_crucial_property_config(crucial_property_config: str):
    """
    Manually set a crucial property config.json\
    See

    :param crucial_property_config: The path to the config.json file
    :return: None
    """
    camorph.crucial_property_config = crucial_property_config

def print_keys():
    """
    Print all available keys for supported formats

    :return: None
    """
    for key in camorph.imported_instances:
        print(key)
