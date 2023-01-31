import warnings
import json
import csv
import copy
import numpy as np

from model.FileHandler import FileHandler
from model.Camera import Camera
from utils import math_utils


class MPEG_OMAF(FileHandler):
    def __init__(self):
        pass

    def crucial_properties(self) -> list[(str, type)]:
        return ['resolution','focal_length_px','principal_point']

    def name(self):
        return "mpeg_omaf"

    def file_number(self):
        return -1

    def read_file(self, input_path: str, *args, **kwargs):
        with open(input_path, 'r') as f:
            mpeg_json = json.loads(f.read())
            cam_arr = []
            # Z Up X Front
            for mcam in mpeg_json['cameras']:
                cam = Camera()
                r = mcam['Rotation'][::-1]
                cam.t = mcam['Position']
                cam.r = math_utils.euler_to_quaternion(r)
                cam.projection_type = mcam['Projection'].lower()
                cam.resolution = mcam['Resolution']
                cam.resolution = mcam['Resolution']
                cam.name = mcam['Name']
                if cam.projection_type == 'perspective':
                    cam.model = 'pinhole'
                    cam.focal_length_px = [mcam['Focal'][0], mcam['Focal'][1]]
                    cam.principal_point = mcam['Principle_point']
                else:
                    cam.focal_length_px = [cam.resolution[0] / 2,cam.resolution[0] / 2]
                    cam.principal_point = [x / 2 for x in cam.resolution]
                cam_arr.append(cam)
            if len(args) == 1 and type(args[0]) == str and args[0].split('.')[-1] == 'csv':
                basecam = next((c for c in cam_arr if c.name == 'viewport'), None)
                if basecam is None:
                    raise ValueError("Camera array needs to contain a camera named viewport as base for the posetrace")
                posetrace_array = []
                with open(args[0],'r') as f:
                    posetrace_data = csv.reader(f)
                    posetrace_data.__next__() # skip heading
                    for idx, row in enumerate(posetrace_data):
                        tr = np.resize(np.asarray(row, dtype='float32'),[2,3])
                        t = tr[0]
                        r = tr[1][::-1]
                        pc = copy.copy(basecam)
                        pc.t += t
                        pc.r = math_utils.euler_to_quaternion(r)
                        pc.name = f'posestrace_{str(idx).zfill(3)}'
                        posetrace_array.append(pc)
                return self.coordinate_from(posetrace_array)

            else:
                cam_arr = list(filter(lambda x: x.name !='viewport', cam_arr))
                return self.coordinate_from(cam_arr)

    def write_file(self, camera_array: list[Camera], output_path: str, file_type=None):
        # from colmap_to_json.py
        json_file = {
            'Version': '2.0',
            'Content_name': 'Colmap dataset',
            'Fps': 1,
            'Frames_number': 1,
            'Informative': {
                'Converted_by': 'camorph',
                'Original_units': 'm',
                'New_units': 'm'},
            'cameras': []
        }
        camera_array = self.coordinate_into(camera_array)
        for cam in camera_array:
            if cam.projection_type not in ['perspective', 'equirectangular', None]:
                warnings.warn(f"Unsupported projection type {cam.projection_type}")
                continue
            json_cam = {
                'Name': cam.name,
                'Position': [float(x) for x in cam.t],
                'Rotation': [float(x) for x in math_utils.quaternion_to_euler(cam.r)],
                'Depthmap': 1,
                'Background': 0,
                'Depth_range': [40.0,70.0],
                'Resolution': cam.resolution,
                'Projection': cam.projection_type.capitalize(),
                'Focal': [cam.focal_length_px[0], cam.focal_length_px[1]],
                'Principle_point': cam.principal_point,
                'BitDepthColor': 8,
                'BitDepthDepth': 16,
                'ColorSpace': 'YUV420',
                'DepthColorSpace': 'YUV420'
            }
            json_file['cameras'].append(json_cam)
        with open(output_path,'w') as f:
            json.dump(json_file, f, indent=4)

    def coordinate_into(self, camera_array: list[Camera]):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['x', 'y', 'z'], cam.t, cam.r, tdir=[1, 0, 0],
                                                                tup=[0, 0, 1])
        return cam_arr

    def coordinate_from(self, camera_array: list[Camera]):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['x', 'y', 'z'], cam.t, cam.r, cdir=[1, 0, 0],
                                                                cup=[0, 0, 1])
        return cam_arr
