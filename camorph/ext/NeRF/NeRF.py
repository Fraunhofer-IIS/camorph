import copy
import fnmatch
import json
import math
import os
import warnings

from PIL import Image
from pyquaternion import Quaternion

from model.Camera import Camera
from model.FileHandler import FileHandler
from utils import math_utils
import numpy as np


def set_local(src, target, targettype=float):
    if type(src) is list:
        for idx, x in enumerate(src):
            if x is not None:
                target[idx] = targettype(x)
    else:
        if src is not None:
            target = targettype(src)

    return target


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
        radial_distorion = [try_get(nerf_json, 'k1'), try_get(nerf_json, 'k2')]
        tangential_distorion = [try_get(nerf_json, 'p1'), try_get(nerf_json, 'p2')]
        principal_point = [try_get(nerf_json, 'cx'), try_get(nerf_json, 'cy')]
        resolution = [try_get(nerf_json, 'w'), try_get(nerf_json, 'h')]
        cams = []
        for c in nerf_json['frames']:
            local_fl = [try_get(c, 'fl_x', 'intrinsics'),try_get(c, 'fl_y', 'intrinsics')]
            local_radial_distortion = [try_get(c, 'k1', 'intrinsics'), try_get(c, 'k2', 'intrinsics')]
            local_tangential_distortion = [try_get(c, 'p1', 'intrinsics'), try_get(c, 'p2', 'intrinsics')]
            local_principal_point = [try_get(c, 'cx', 'intrinsics'), try_get(c, 'cy', 'intrinsics')]
            local_resolution = [try_get(c, 'w', 'intrinsics'), try_get(c, 'h', 'intrinsics')]
            cam = Camera()
            transmat = np.asarray(c['transform_matrix'])
            cam.t = transmat[:, -1][:-1]
            # NeRF rotations are not precise enough for our quaternions
            # therefore we need to construct a pure orthogonal matrix
            warnings.warn("NeRF did not supply a perfect orthogonal matrix")
            rotmat = transmat[:-1, :-1]
            v1 = rotmat[0]
            v2 = rotmat[1]
            # compute our own orthogonal vector with as much information as possible
            if v1[2] != 0:
                v2 = [v2[0], v2[1], (-v1[0] * v2[0] - v1[1] * v2[1]) / v1[2]]
            elif v1[1] != 0:
                v2 = [v2[0], (-v1[0] * v2[0] - v1[2] * v2[2]) / v1[1], v2[2]]
            else:
                v2 = [(-v1[1] * v2[1] - v1[2] * v2[2]) / v1[0], v2[1], v2[2]]
            v1 = v1 / np.linalg.norm(v1)
            v2 = v2 / np.linalg.norm(v2)
            corrected = np.asarray([v1, v2, np.cross(v1, v2)])
            cam.r = Quaternion(matrix=corrected)
            dirname = os.path.dirname(c['file_path'])
            if not os.path.isabs(dirname):
                curdir = os.getcwd()
                os.chdir(os.path.dirname(input_path))
                dirname = os.path.abspath(dirname)
                os.chdir(curdir)

            if None not in radial_distorion:
                cam.radial_distortion = [float(x) for x in radial_distorion]
                cam.model = 'brown'
            set_local(local_radial_distortion, cam.radial_distortion)
            if None not in tangential_distorion:
                cam.tangential_distortion = [float(x) for x in tangential_distorion]
                cam.model = 'brown'
            set_local(local_tangential_distortion, cam.tangential_distortion)

            if None not in principal_point:
                cam.principal_point = [float(x) for x in principal_point]
            set_local(local_principal_point, cam.principal_point)

            bname = os.path.basename(c['file_path'])
            if 'posetrace' in kwargs and kwargs['posetrace'] is True:
                img = bname
            elif len(bname.split('.')) > 1:
                img = next(filter(lambda o: fnmatch.fnmatch(o, bname), os.listdir(dirname)),None)
            else:
                img = next(filter(lambda o: fnmatch.fnmatch(o, bname + ".*[!xmp]"), os.listdir(dirname)),None)
            cam.name = bname

            warningstring = f"Image {c['file_path']} does not exist, cannot set parameter(s): "
            imexists = True

            if img is not None:
                cam.source_image = os.path.join(dirname, img)
            else:
                should_warn = False
                warningstring += 'source_image'

            if None not in resolution:
                cam.resolution = resolution
            elif imexists:
                with Image.open(cam.source_image) as i:
                    cam.resolution = i.size
            else:
                warningstring += ' resolution'

            set_local(local_resolution, cam.resolution, int)

            if fl_x is not None:
                cam.focal_length_px = [fl_x,fl_y]

            elif imexists:
                if camera_angle_y is None:
                    cam.focal_length_px = [.5 * cam.resolution[0] / np.tan(.5 * camera_angle_x),
                                            .5 * cam.resolution[0] / np.tan(.5 * camera_angle_x)]
                else:
                    cam.focal_length_px = [.5 * cam.resolution[0] / np.tan(.5 * camera_angle_x),
                                            .5 * cam.resolution[1] / np.tan(.5 * camera_angle_y)]
            else:
                warningstring += ' focal_length'
            cam.focal_length_px = set_local(local_fl, cam.focal_length_px)

            if cam.resolution is not None:
                if cam.resolution[0] > cam.resolution[1]:
                    cam.sensor_size = (36, (36 / cam.resolution[0]) * cam.resolution[1])
                else:
                    cam.sensor_size = ((36 / cam.resolution[1]) * cam.resolution[0], 36)
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
            "cx": lambda x: try_get(x.principal_point, 0, default=0.0),
            "cy": lambda x: try_get(x.principal_point, 1, default=0.0),
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
                source_image = os.path.relpath(source_image,output_path)

            json_cam = {
                'intrinsics': {},
                'file_path': source_image,
                'rotation': 0,
                'transform_matrix': trans_mat.tolist()
            }
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
