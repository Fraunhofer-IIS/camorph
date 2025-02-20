import copy
import fnmatch
import json
import math
import os
import warnings

from PIL import Image
from pyquaternion import Quaternion

from camorph.lib.model.Camera import Camera
from camorph.lib.model.FileHandler import FileHandler
from camorph.lib.utils import math_utils
import numpy as np


def set_local(src, target, cam, targettype=float):
    if type(src) is list:
        if src is not None:
            if getattr(cam, target) is None:
                srcarr = [None for x in src]
            else:
                srcarr = getattr(cam,target)
            
            for idx, x in enumerate(src):
                if x is not None:
                    srcarr[idx] = x
            setattr(cam,target,srcarr)
    else:
        if src is not None:
            setattr(cam,target,targettype(src))


def try_get(obj, key,obj_key=None, default=None):
    try:
        if obj_key is None:
            return obj[key]
        else:
            return obj[obj_key][key]
    except (KeyError, TypeError, IndexError):
        return default


class NeRF(FileHandler):
    def __init__(self):
        pass

    def crucial_properties(self) -> list[(str, type)]:
        return ['focal_length_px', 'resolution', 'source_image']

    def name(self):
        return "nerf"

    def file_number(self):
        return 1

    def read_file(self, input_path: str, **kwargs):
        with open(input_path, 'r') as f:
            nerf_json = json.loads(f.read())

        camera_angle_x = try_get(nerf_json,'camera_angle_x')
        camera_angle_y = try_get(nerf_json,'camera_angle_y')
        fl_x = try_get(nerf_json, 'fl_x')
        fl_y = try_get(nerf_json, 'fl_y')
        radial_distorion = [try_get(nerf_json, 'k1'), try_get(nerf_json, 'k2'), try_get(nerf_json, 'k3'), try_get(nerf_json, 'k4')]
        tangential_distorion = [try_get(nerf_json, 'p1'), try_get(nerf_json, 'p2')]
        principal_point = [try_get(nerf_json, 'cx'), try_get(nerf_json, 'cy')]
        resolution = [try_get(nerf_json, 'w'), try_get(nerf_json, 'h')]
        cams = []
        for c in nerf_json['frames']:
            local_fl = [try_get(c, 'fl_x', 'intrinsics'),try_get(c, 'fl_y', 'intrinsics')]
            local_radial_distortion = [try_get(c, 'k1', 'intrinsics'), try_get(c, 'k2', 'intrinsics'), try_get(c, 'k3', 'intrinsics'), try_get(c, 'k4', 'intrinsics')]
            local_tangential_distortion = [try_get(c, 'p1', 'intrinsics'), try_get(c, 'p2', 'intrinsics')]
            local_principal_point = [try_get(c, 'cx', 'intrinsics'), try_get(c, 'cy', 'intrinsics')]
            local_resolution = [try_get(c, 'w', 'intrinsics'), try_get(c, 'h', 'intrinsics')]
            local_camera_angle = [try_get(nerf_json,'camera_angle_x'),try_get(nerf_json,'camera_angle_y')]
            exif = try_get(c, 'exif')
            mask = try_get(c, 'mask_path')
            cam = Camera()
            transmat = np.asarray(c['transform_matrix'])
            cam.t = transmat[:, -1][:-1]
            rotmat = transmat[:-1, :-1]
            cam.r = math_utils.rotation_matrix_to_quaternion(rotmat)
            dirname = os.path.dirname(c['file_path'])
            if not os.path.isabs(dirname):
                curdir = os.getcwd()
                os.chdir(os.path.dirname(input_path))
                dirname = os.path.abspath(dirname)
                os.chdir(curdir)


            cam.radial_distortion = [float(x) if x is not None else x for x in radial_distorion]
            set_local(local_radial_distortion, "radial_distortion", cam)

            cam.tangential_distortion = [float(x) if x is not None else x for x in tangential_distorion]
            set_local(local_tangential_distortion, "tangential_distortion", cam)

            cam.radial_distortion = [x for x in cam.radial_distortion if x is not None]
            cam.tangential_distortion = [x for x in cam.tangential_distortion if x is not None]

            if len(cam.radial_distortion) > 0 or len(cam.tangential_distortion) > 0:
                cam.model='brown'

            bname = os.path.basename(c['file_path'])
            if 'posetrace' in kwargs and kwargs['posetrace'] is True:
                img = bname
            elif len(bname.split('.')) > 1:
                img = next(filter(lambda o: fnmatch.fnmatch(o, bname), os.listdir(dirname)),None)
            else:
                img = next(filter(lambda o: fnmatch.fnmatch(o, bname + ".*[!xmp]"), os.listdir(dirname)),None)
            cam.name = bname

            if img is not None:
                cam.source_image = os.path.join(dirname, img)
            else:
                warnings.warn("Source image could not be read, file checks cannot be performed")
                cam.source_image = c['file_path']

            if None not in resolution:
                cam.resolution = [resolution[0], resolution[1]] # To avoid shallow copy issues
            else:
                with Image.open(cam.source_image) as i:
                    cam.resolution = i.size

            set_local(local_resolution, "resolution", cam, int)

            if None not in principal_point:
                cam.principal_point = [float(x) for x in principal_point]
            if None not in local_principal_point:
                set_local(local_principal_point, "principal_point", cam)
            if cam.principal_point is None:
                principal_point_from_resolution = [side_length / 2 for side_length in cam.resolution]
                set_local(principal_point_from_resolution, "principal_point", cam)

            if fl_x is not None:
                if fl_y is not None:
                    cam.focal_length_px = [fl_x,fl_y]
                else:
                    cam.focal_length_px = [fl_x,fl_x]
            set_local(local_fl, "focal_length_px", cam)

            if None in cam.focal_length_px:
                if camera_angle_x is None:
                    camera_angle_x = local_camera_angle[0]
                if camera_angle_y is None:
                    camera_angle_y = local_camera_angle[1]
                if camera_angle_y is None:
                    cam.focal_length_px = [.5 * cam.resolution[0] / np.tan(.5 * camera_angle_x),
                                            .5 * cam.resolution[0] / np.tan(.5 * camera_angle_x)]
                else:
                    cam.focal_length_px = [.5 * cam.resolution[0] / np.tan(.5 * camera_angle_x),
                                            .5 * cam.resolution[1] / np.tan(.5 * camera_angle_y)]

            if cam.resolution is not None:
                if cam.resolution[0] > cam.resolution[1]:
                    cam.sensor_size = (36, (36 / cam.resolution[0]) * cam.resolution[1])
                else:
                    cam.sensor_size = ((36 / cam.resolution[1]) * cam.resolution[0], 36)

            cam.exif = exif

            cam.mask = mask
            cams.append(cam)

        return self.coordinate_from(cams)

    def write_file(self, camera_array: list[Camera], output_path: str, file_type=None):
        # from colmap_to_json.py
        cam1 = camera_array[0]
        attr_fn = {
            'camera_angle_x': lambda x: 2 * math.atan2(x.resolution[0] / 2, x.focal_length_px[0]),
            'camera_angle_y': lambda x: 2 * math.atan2(x.resolution[1] / 2, x.focal_length_px[1]),
            "fl_x": lambda x: x.focal_length_px[0],
            "fl_y": lambda x: x.focal_length_px[1],
            "k1": lambda x: try_get(x.radial_distortion, 0, default=0.0),
            "k2": lambda x: try_get(x.radial_distortion, 1, default=0.0),
            "k3": lambda x: try_get(x.radial_distortion, 2, default=0.0),
            "p1": lambda x: try_get(x.tangential_distortion, 0, default=0.0),
            "p2": lambda x: try_get(x.tangential_distortion, 1, default=0.0),
            "p3": lambda x: try_get(x.tangential_distortion, 2, default=0.0),
            "cx": lambda x: try_get(x.principal_point, 0, default=x.resolution[0]/2.0),
            "cy": lambda x: try_get(x.principal_point, 1, default=x.resolution[1]/2.0),
            "w": lambda x: int(x.resolution[0]),
            "h": lambda x: int(x.resolution[1])
        }

        json_file = {}
        for attr in attr_fn:
            json_file[attr] = attr_fn[attr](cam1)
        json_file['aabb_scale'] = 1
        json_file['frames'] = []

        camera_array = self.coordinate_into(camera_array)
        for cam in camera_array:
            trans_mat = np.identity(4)
            trans_mat[:-1, :-1] = cam.r.rotation_matrix
            trans_mat[:, -1][:-1] = cam.t

            source_image = cam.source_image

            if os.path.isabs(cam.source_image):
                warnings.warn("Camorph needs absolute image Paths. Relative paths are automatically calculated when saving to NeRF")
                tmp_output_path = output_path
                if not os.path.isdir(tmp_output_path):
                    tmp_output_path = os.path.split(output_path)[0]

                # Fallback to absolute path in case source images are on different mount
                try:
                    source_image = os.path.relpath(source_image,tmp_output_path)
                except(ValueError):
                    warnings.warn("Output path is on different mount as compared to the source images. Creating relative paths not possible, fallback to absolute paths!")
                    
            json_cam = {
                'intrinsics': {},
                'file_path': source_image,
                'rotation': 0,
                'transform_matrix': trans_mat.tolist()
            }
            if cam.exif is not None:
                json_cam['exif'] = cam.exif
            if cam.mask is not None:
                json_cam['mask'] = cam.mask
            json_file['frames'].append(json_cam)

        # Write individual intrinsics
        for k in attr_fn:
            base_attr = json_file[k]
            for cam in camera_array:
                if abs(attr_fn[k](cam) - base_attr) > 0.001:
                    for idx, json_cam in enumerate(json_file['frames']):
                        json_cam['intrinsics'][k] = attr_fn[k](camera_array[idx])
                    break

        with open(output_path, 'w') as f:
            json.dump(json_file, f, indent=4)

    def coordinate_into(self, camera_array: list[Camera]):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['y', '-x', 'z'], cam.t, cam.r, cdir=[0, 0, -1],
                                                                 cup=[0, 1, 0], transpose=True)
        return cam_arr

    def coordinate_from(self, camera_array: list[Camera]):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['y', '-x', 'z'], cam.t, cam.r, cdir=[0, 0, -1],
                                                                 cup=[0, 1, 0])
        return cam_arr
