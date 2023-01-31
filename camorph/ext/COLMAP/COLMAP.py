import os
import warnings
from os.path import basename
import copy

from numpy import ndarray

import utils.math_utils as math_utils
from model.Camera import Camera
from utils.file_utils import get_files_in_dir

from model.FileHandler import FileHandler
from .util import ReaderSyntacticUtil as rsu, WriterSyntacticUtil


class COLMAP(FileHandler):
    """
    This is the docstring for the colmap class
    """

    def crucial_properties(self) -> list[str]:
        return ['source_image','resolution','principal_point','focal_length_px']

    def name(self):
        return "COLMAP"

    def file_number(self):
        return 2

    def read_file(self, *path, **kwargs):
        if len(path) == 1:
            path = path[0]
            if 'images.bin' in get_files_in_dir(path):
                input_path_images = os.path.join(path, 'images.bin')
            elif 'images.txt' in get_files_in_dir(path):
                input_path_images = os.path.join(path, 'images.txt')
            else:
                raise Exception('No images file in path ', path)

            if 'cameras.bin' in get_files_in_dir(path):
                input_path_cameras = os.path.join(path, 'cameras.bin')
            elif 'cameras.txt' in get_files_in_dir(path):
                input_path_cameras = os.path.join(path, 'cameras.txt')
            else:
                raise Exception('No cameras file in path ', path)
        elif len(path) == 2:
            input_path_images, input_path_cameras = path
        else:
            raise Exception('Unsupported number of arguments, expected 1-2, got ', len(path))


        images = rsu.read_images(input_path_images)
        cams = rsu.read_cameras(input_path_cameras)

        cam_arr = []
        for img in images:
            colmap_cam = next(c for c in cams if(img.cam_id == c.cam_id))
            cam = Camera()
            cam.autocompute = True
            cam.r = img.q.inverse
            cam.t = -(img.q.inverse.rotate(img.t))
            cam.resolution = colmap_cam.res
            cam.name = basename(img.name)
            cam.projection_type = 'perspective'
            if cam.resolution[0] > cam.resolution[1]:
                cam.sensor_size = (36,(36/cam.resolution[0])*cam.resolution[1])
            else:
                cam.sensor_size = ((36 / cam.resolution[1]) * cam.resolution[0], 36)
            # COLMAP usually has relative paths, so we cannot set the source image directly
            if colmap_cam.type == "SIMPLE_PINHOLE":
                cam.model = 'pinhole'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[0])]
                cam.principal_point = [float(colmap_cam.params[1]), float(colmap_cam.params[2])]
            elif colmap_cam.type == "PINHOLE":
                # different focal lengths not supported
                cam.model = 'pinhole'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[1])]
                cam.principal_point = [float(colmap_cam.params[2]), float(colmap_cam.params[3])]
            elif colmap_cam.type == "SIMPLE_RADIAL":
                cam.model = 'brown'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[0])]
                cam.principal_point = [float(colmap_cam.params[1]), float(colmap_cam.params[2])]
                cam.radial_distortion = [float(colmap_cam.params[3])]
            elif colmap_cam.type == "RADIAL":
                cam.model = 'brown'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[0])]
                cam.principal_point = [float(colmap_cam.params[1]), float(colmap_cam.params[2])]
                cam.radial_distortion = [float(x) for x in colmap_cam.params[3:]]
            elif colmap_cam.type == "OPENCV":
                cam.model = 'brown'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[1])]
                cam.principal_point = [float(colmap_cam.params[2]), float(colmap_cam.params[3])]
                cam.radial_distortion = [float(x) for x in colmap_cam.params[4:6]]
                cam.tangential_distortion = [float(x) for x in colmap_cam.params[6:8]]
            elif colmap_cam.type == "FULL_OPENCV":
                cam.model = 'brown'
                # different focal lengths not supported
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[1])]
                cam.principal_point = [float(colmap_cam.params[2]), float(colmap_cam.params[3])]
                cam.radial_distortion = [float(x) for x in colmap_cam.params[4:5]]
                cam.tangential_distortion = [float(x) for x in colmap_cam.params[6:8]]
                cam.radial_distortion.extend([float(x) for x in colmap_cam.params[8:12]])
            #https://docs.opencv.org/3.4/db/d58/group__calib3d__fisheye.html
            elif colmap_cam.type == "OPENCV_FISHEYE":
                cam.model = 'opencv_fisheye4'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[1])]
                cam.principal_point = [float(colmap_cam.params[2]), float(colmap_cam.params[3])]
                cam.radial_distortion = [float(x) for x in colmap_cam.params[4:]]
            elif colmap_cam.type == "SIMPLE_RADIAL_FISHEYE":
                cam.model = 'opencv_fisheye1'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[0])]
                cam.principal_point = [float(colmap_cam.params[1]), float(colmap_cam.params[2])]
                cam.radial_distortion = float(colmap_cam.params[3])
            elif colmap_cam.type == "RADIAL_FISHEYE":
                cam.model = 'opencv_fisheye2'
                cam.focal_length_px = [float(colmap_cam.params[0]),float(colmap_cam.params[0])]
                cam.principal_point = [float(colmap_cam.params[1]), float(colmap_cam.params[2])]
                cam.radial_distortion = [float(x) for x in colmap_cam.params[3:]]
            else:
                raise Exception(f"Unsupported COLMAP type ${colmap_cam.type}")

            if os.path.isabs(img.name):
                cam.source_image = img.name
            else:
                images_dir = os.path.join(os.path.dirname(os.path.dirname(input_path_images)), 'images')
                if not os.path.isdir(images_dir):
                    warnings.warn(
                        'Camorph could not locate the COLMAP images folder. When writing, make sure to supply a config.json')
                else:
                    imgfile = os.path.join(images_dir, cam.name)
                    if os.path.isfile(imgfile):
                        cam.source_image = imgfile
                    else:
                        warnings.warn(f"Images folder found, but image {cam.name} not found")

            cam_arr.append(cam)

        cam_arr = self.coordinate_from(cam_arr)

        return cam_arr



    def write_file(self, camera_array, output_path, file_type = None):
        if file_type == 'txt' or file_type is None:
            WriterSyntacticUtil.write_cameras_file_txt(camera_array, output_path)
            WriterSyntacticUtil.write_images_file_txt(camera_array, output_path)
        elif file_type == 'bin':
            WriterSyntacticUtil.write_cameras_file_bin(camera_array, output_path)
            WriterSyntacticUtil.write_images_file_bin(camera_array, output_path)
        else:
            raise Exception(f"Unsupported file type: ${file_type}")

    def coordinate_into(self, camera_array):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['-y', '-z', 'x'], cam.t, cam.r, tdir=[0, 0, 1],
                                                                tup=[0, -1, 0], transpose=True)
        return cam_arr

    def coordinate_from(self, camera_array):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['-y', '-z', 'x'], cam.t, cam.r, cdir=[0, 0, 1], cup = [0,-1,0])
        return cam_arr
