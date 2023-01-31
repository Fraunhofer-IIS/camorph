import copy
import json
import warnings
import os
from .util import ReaderSyntacticUtil, WriterSyntacticUtil
from model.Camera import Camera
from model.FileHandler import FileHandler
from utils import math_utils



class Meshroom(FileHandler):
    def __init__(self):
        pass

    def crucial_properties(self) -> list[(str, type)]:
        return ['source_image','resolution','sensor_size','focal_length_px']

    def name(self):
        return "meshroom"

    def file_number(self):
        return 1

    def read_file(self, input_path: str, **kwargs):
        suffix = input_path[input_path.rfind('.'):]
        if suffix == '.mg':
            cams = []
            with open(input_path, 'r') as f:
                meshroom_json = json.loads(f.read())
                graph = meshroom_json['graph']
                nodes = []
                for key in graph:
                    node = graph[key]
                    node['name'] = key
                    nodes.append(graph[key])
                for node in nodes:
                    if node['nodeType'] == 'StructureFromMotion':
                        uid = node['uids']['0']
                        sfm_folder = os.path.join(input_path[:input_path.rfind(os.path.sep)], 'MeshroomCache', 'StructureFromMotion', str(uid), 'cameras.sfm')
                        try:
                            cams.extend(ReaderSyntacticUtil.read_sfm(sfm_folder))
                        except Exception:
                            #raise Exception
                            warnings.warn('sfm file does not exist for node {}'.format(node['name']))
        elif suffix == '.sfm':
            cams = ReaderSyntacticUtil.read_sfm(input_path)
        else:
            raise Exception('Unsupported File Format ', suffix)
        return self.coordinate_from(cams)

    def write_file(self, camera_array: list[Camera], output_path: str, file_type = None):
        cam_arr = self.coordinate_into(camera_array)
        sfm_json = WriterSyntacticUtil.build_file(cam_arr)
        with open(output_path, "w+") as file:
            file.write(sfm_json)


    def coordinate_into(self, camera_array: list[Camera]):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['y', 'z', 'x'], cam.t, cam.r, cdir=[0, 0, -1],
                                                                cup=[0, 1, 0], transpose=True)
        return cam_arr

    def coordinate_from(self, camera_array: list[Camera]):
        cam_arr = copy.deepcopy(camera_array)
        for cam in cam_arr:
            cam.t, cam.r = math_utils.convert_coordinate_systems(['y', 'z', 'x'], cam.t, cam.r, cdir=[0, 0, -1],
                                                                cup=[0, 1, 0])
        return cam_arr
