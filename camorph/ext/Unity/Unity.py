import math
import warnings

import numpy as np

from .util import ReaderSyntacticUtil, ReaderSemanticUtil, WriterSyntacticUtil
from model.Camera import Camera
from utils import math_utils
from model.FileHandler import FileHandler


class Unity(FileHandler):

    def crucial_properties(self) -> list[(str, type)]:
        return ['fov']

    def name(self):
        return "unity"

    def file_number(self):
        return 1

    def read_file(self, input_path, **kwargs):
        with open(input_path, "r") as f:
            txt = f.read()
        game_objs, cameras, transforms = ReaderSyntacticUtil.get_unity_from_yaml(txt)
        # we dont support cameras in prefabs for now
        ret_cams = []
        for cam in cameras:
            # find corresponding transform
            transform = next(x for x in transforms if x['m_GameObject']['fileID'] == cam['m_GameObject']['fileID'])
            game_obj = next(x for x in game_objs if x['obj_id'] == cam['m_GameObject']['fileID'])
            translation, rotation = ReaderSemanticUtil.apply_transform_rec(transform, transforms)
            c = Camera()
            c.r = rotation
            c.t = translation
            c.name = game_obj['m_Name']

            c.projection_type = 'orthographic' if cam['orthographic'] == 1 else 'perspective'
            c.model = 'orthographic' if c.projection_type == 'orthographic' else 'pinhole'

            c.focal_length_mm = [cam['m_FocalLength'], cam['m_FocalLength']]
            c.sensor_size = [cam['m_SensorSize']['x'], cam['m_SensorSize']['y']]
            c.lens_shift = [cam['m_LensShift']['x'], cam['m_LensShift']['y']]

            fov_axis_mode = cam['m_FOVAxisMode']
            if fov_axis_mode == 1:
                c.fov = (np.radians(cam['field of view']), c.sensor_size[1]*np.radians(cam['field of view'])/c.sensor_size[0])
            else:
                c.fov = (c.sensor_size[0] * np.radians(cam['field of view']) / c.sensor_size[1]), np.radians(cam['field of view'])
            computed_fov = 2 * math.atan2(c.sensor_size[0], 2 * c.focal_length_mm[0])
            epsilon = 0.01
            if abs(computed_fov - c.fov[0]) > epsilon:
                warnings.warn('Focal length and field of view from Unity do not match. Calculating focal length from field of view')
                c.focal_length_mm = [c.sensor_size[0] / (2 * math.atan2(c.fov[0], 2)),
                                     c.sensor_size[1] / (2 * math.atan2(c.fov[1], 2))]


            ret_cams.append(c)

        ret_cams = self.coordinate_from(ret_cams)
        return ret_cams

    def write_file(self, camera_array, output_path, file_type = None):
        camera_array = self.coordinate_into(camera_array)
        file = WriterSyntacticUtil.build_file(camera_array)
        path = output_path
        with open(path, 'w') as f:
            f.write(file)

    def coordinate_into(self, camera_array):
        cam_arr = camera_array.copy()
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['y', 'z', '-x'], cam.t, cam.r, tdir=[0, 0, 1],
                                                                tup=[0, 1, 0], transpose = True)
        return cam_arr

    def coordinate_from(self, camera_array):
        cam_arr = camera_array.copy()
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['y', 'z', '-x'], cam.t, cam.r, cdir=[0, 0, 1],
                                                                cup=[0, 1, 0])

        return cam_arr
