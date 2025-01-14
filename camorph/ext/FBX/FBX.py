import os.path
import sys
import warnings
import numpy as np
import re

from camorph.lib.model.FileHandler import FileHandler
from camorph.lib.model.Camera import Camera
from .model import *
from .util import ReaderSemanticUtil
from .util import ReaderSyntacticUtil
from .util import WriterSyntacticUtil
from camorph.lib.utils import math_utils
from camorph.lib.utils import bin_reader_utils
from camorph.lib.utils import file_utils


class FBX(FileHandler):
    def __init__(self):
        self.debug_text = []
        pass

    def crucial_properties(self) -> list[(str, type)]:
        return []

    def name(self):
        return "fbx"

    def file_number(self):
        return 1

    def read_file(self, input_path, **kwargs):
        fbx_obj = FBXNode()
        file_size = os.path.getsize(input_path)
        with open(input_path, mode='rb') as f:
            fbx_obj['header'] = ReaderSyntacticUtil.read_header(f)
            FBXVersion = fbx_obj['header'][2]
            while file_size - f.tell() > 200:  # TODO magic fbx footer ?
                val = ReaderSyntacticUtil.read_node_record(f, file_size, FBXVersion)
                if val[0] is not None:
                    [nested_obj, uid] = val
                    fbx_obj[uid] = nested_obj
            footer = f.read(file_size - f.tell())
        camarr = []

        #get camera defaults
        obj_types = fbx_obj['Definitions']['ObjectType']
        cam_defaults = next((x for x in obj_types if 'PropertyTemplate' in x and x['PropertyTemplate'][0]['pname'] == 'FbxCamera'), None)
        if cam_defaults is None:
            warnings.warn("No cameras in scene")
            return None
        else:
            cam_defaults = cam_defaults['PropertyTemplate'][0]['Properties70'][0]
        default_optical_center = (cam_defaults['OpticalCenterX'][0].pvalue[0],cam_defaults['OpticalCenterY'][0].pvalue[0]) if 'OpticalCenterX' in cam_defaults else (0,0)
        default_resolution = (cam_defaults['AspectWidth'][0].pvalue[0],cam_defaults['AspectHeight'][0].pvalue[0])  if 'AspectWidth' in cam_defaults else (1920,1080)
        default_sensor_size = (math_utils.inch_to_mm(cam_defaults['FilmWidth'][0].pvalue[0]),
                               math_utils.inch_to_mm(cam_defaults['FilmHeight'][0].pvalue[0]))   if 'AspectWidth' in cam_defaults else (36,24)
        default_focal_length = [cam_defaults['FocalLength'][0].pvalue[0] if 'AspectWidth' in cam_defaults else 50
                                ,cam_defaults['FocalLength'][0].pvalue[0] if 'AspectWidth' in cam_defaults else 50]
        default_projection_type = ('perspective' if cam_defaults['CameraProjectionType'][0].pvalue[0] == 0 else 'orthogonal')   if 'CameraProjectionType' in cam_defaults else 'perspective'
        root_node = FBXHierarchyNode(0)

        coordinate_system = ReaderSemanticUtil.get_coordinate_system(fbx_obj)


        ReaderSemanticUtil.build_hierarchy_tree([x for x in fbx_obj['Connections']], fbx_obj['Objects'],
                                                root_node)  # root node is 0
        transforms = dict()
        # root node, model node, transform, rotation, children
        transforms[0] = [root_node.object, None, np.array([0, 0, 0]), np.identity(3), None]
        ReaderSemanticUtil.resolve_hierarchy(root_node, transforms)

        def inch_to_mm(inch):
            return 25.4 * inch

        for cam in [transforms[x] for x in transforms if transforms[x][1] == 'Camera']:
            # set transform and rotation
            c = Camera()
            c.autocompute = True
            c.t = cam[2]
            c.r = cam[3]
            # camera direction in fbx is [1,0,0]
            [c.t, c.r] = math_utils.convert_coordinate_systems(coordinate_system,c.t, c.r, cdir = np.array([1, 0, 0]), transpose=True)
            c.name = cam[0].ptype.split('\u0000')[0]
            # set other parameters
            attributes = next(x for x in cam[4] if len(x.object) == 1 and type(x.object[0]) == FBXNodeObject).object[0].Properties70[0]


            c.resolution = default_resolution if 'AspectWidth' not in attributes \
                else (attributes['AspectWidth'][0].pvalue[0], attributes['AspectHeight'][0].pvalue[0])

            c.sensor_size = default_sensor_size if 'FilmWidth' not in attributes \
                else (math_utils.inch_to_mm(attributes['FilmWidth'][0].pvalue[0]),
                      math_utils.inch_to_mm(attributes['FilmHeight'][0].pvalue[0]))

            # principal_point
            optical_center = default_optical_center
            if 'OpticalCenterX' in attributes:
                optical_center = (attributes['OpticalCenterX'][0].pvalue[0],
                                  attributes['OpticalCenterY'][0].pvalue[0])
                c.principal_point = ((c.resolution[0] / 2) + optical_center[0], (c.resolution[1] / 2) + optical_center[1])
            elif 'FrontPlaneOffsetX' in attributes and 'FrontPlaneOffsetY' in attributes:
                c.lens_shift = (-inch_to_mm(attributes['FrontPlaneOffsetX'][0].pvalue[0]/c.sensor_size[0]),
                                inch_to_mm(attributes['FrontPlaneOffsetY'][0].pvalue[0]/c.sensor_size[1]))
            elif 'FilmOffsetX' in attributes and 'FilmOffsetY' in attributes:
                c.lens_shift = (inch_to_mm(attributes['FilmOffsetX'][0].pvalue[0]/c.sensor_size[0]),
                                inch_to_mm(attributes['FilmOffsetY'][0].pvalue[0]/c.sensor_size[1]))
            else :
                c.principal_point = (c.resolution[0]/2,c.resolution[1]/2)

            if 'NearPlane' in attributes and 'FarPlane' in attributes:
                c.near_far_bounds = (attributes['NearPlane'][0].pvalue[0]/100,attributes['FarPlane'][0].pvalue[0]/100)

            if abs(c.sensor_size[0]/c.sensor_size[1] - c.resolution[0]/c.resolution[1]) > 0.001:
                warnings.warn("Sensor size aspect ratio did not match resolution aspect ratio (default blender behaviour),"
                              " calculated sensor size based on resolution aspect ratio.")
                c.sensor_size =(c.sensor_size[0], c.sensor_size[0] * c.resolution[1] / c.resolution[0])

            c.focal_length_mm = default_focal_length if 'FocalLength' not in attributes \
                else [attributes['FocalLength'][0].pvalue[0],attributes['FocalLength'][0].pvalue[0]]

            c.projection_type = default_projection_type if 'CameraProjectionType' not in attributes \
                else ('perspective' if attributes['CameraProjectionType'][0].pvalue[0] == 0 else 'orthogonal')
            if 'FileName' in attributes:
                c.source_image = attributes['FileName']
                c.source_image = re.sub(r"(?<!^)\\\\", r"\\", c.source_image)

            if c.source_image is None and 'posetrace' in kwargs and kwargs['posetrace']:
                c.source_image = c.name
            camarr.append(c)

        return camarr

    def write_file(self, camera_array, output_path, file_type = None):
        file = WriterSyntacticUtil.build_file(camera_array)
        path = output_path
        with open(path, 'wb') as f:
            f.write(file)

    def coordinate_into(self, camera_array):
        pass

    def coordinate_from(self, camera_array):
        pass

    # DEBUG
    def read_file_debug(self, input_path):

        fbx_obj = FBXNode()
        file_size = os.path.getsize(input_path)
        with open(input_path, mode='rb') as f:
            fbx_obj['header'] = ReaderSyntacticUtil.read_header(f)
            FBXVersion = fbx_obj['header'][2]
            while file_size - f.tell() > 200:  # TODO magic fbx footer ?
                val = self.read_node_record_debug(f, file_size, FBXVersion)
                if val is not None:
                    [nested_obj, name] = val
                    fbx_obj[name] = nested_obj

    def read_node_record_debug(self, f, file_size, FBXVersion, depth=0):
        nested_obj = FBXNode()
        if (file_size - f.tell()) < 200:  # TODO magic fbx footer number
            f.read(file_size - f.tell())
            return [None, '']

        # read node header
        if FBXVersion < 7500:
            offset = bin_reader_utils.read_uint32(f)
            num_properties = bin_reader_utils.read_uint32(f)
            property_list_len = bin_reader_utils.read_uint32(f)
        else:
            offset = bin_reader_utils.read_uint64(f)
            num_properties = bin_reader_utils.read_uint64(f)
            property_list_len = bin_reader_utils.read_uint64(f)

        name_len = bin_reader_utils.read_uint8(f)
        name = bin_reader_utils.read_string(f, name_len)
        debug_offset = "".join(["   " for x in range(0, depth)])
        #print(debug_offset + name)
        self.debug_text.append(debug_offset + name)

        # default handling for unsupported nodes
        props = []
        for i in range(0, num_properties):
            # props.append(self.read_property(f))
            ReaderSyntacticUtil.read_property_debug(f, depth + 1, self.debug_text)

        self.read_child_debug(f, offset, file_size, depth + 1, nested_obj, FBXVersion)
        nested_obj['props'] = props
        return [nested_obj, name]

    def read_child_debug(self, f, offset, file_size, depth, nested_obj, FBXVersion):
        # only way to check if nested_list is set is to check
        # if the offset is longer than the current position
        cur_pos = f.tell()
        endlen = 13 if FBXVersion < 7500 else 25
        endbytes = b''.join([b'\x00' for x in range(endlen)])
        while cur_pos < offset:
            if file_utils.peek(f, endlen) == endbytes and offset - cur_pos <= endlen:
                f.read(endlen)
                cur_pos = offset
                break
            [second_level_obj, second_level_name] = self.read_node_record_debug(f, file_size, FBXVersion, depth + 1)
            cur_pos = f.tell()
            if second_level_obj is not None:
                nested_obj[second_level_name] = second_level_obj
