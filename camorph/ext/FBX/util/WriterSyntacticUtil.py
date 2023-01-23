from datetime import datetime
from typing import Union
import random

from pyquaternion import Quaternion

from model.Camera import Camera
from utils import bin_writer_utils as bfw, math_utils as mu, math_utils, file_utils

primitive_types = {
    'Y': lambda i: bfw.get_int16(i),
    'C': lambda i: bfw.get_bool(i),
    'I': lambda i: bfw.get_int32(i),
    'F': lambda i: bfw.get_float32(i),
    'D': lambda i: bfw.get_float64(i),
    'L': lambda i: bfw.get_int64(i)
}

complex_types = {
    'S': lambda s: bfw.get_string(s),
    'R': lambda r: r
}

type_lengths = {
    'Y': lambda x: 2,
    'C': lambda x: 1,
    'I': lambda x: 4,
    'F': lambda x: 4,
    'D': lambda x: 8,
    'L': lambda x: 8,
    'S': lambda s: len(s),
    'R': lambda r: len(r)
}


def build_file(cams) -> bytes:
    file = get_header()

    # Static Header Extension
    n1 = FBXFileNode('FBXHeaderExtension')
    n1_1 = FBXFileNode('FBXHeaderVersion', [FBXFileProperty('I', 1003)])
    n1_2 = FBXFileNode('FBXVersion', [FBXFileProperty('I', 7400)])
    n1_3 = FBXFileNode('EncryptionType', [FBXFileProperty('I', 0)])
    n1_4 = FBXFileNode('CreationTimeStamp')
    now = datetime.now()
    n1_4_1 = FBXFileNode('Version', [FBXFileProperty('I', 1000)])
    n1_4_2 = FBXFileNode('Year', [FBXFileProperty('I', now.year)])
    n1_4_3 = FBXFileNode('Month', [FBXFileProperty('I', now.month)])
    n1_4_4 = FBXFileNode('Day', [FBXFileProperty('I', now.day)])
    n1_4_5 = FBXFileNode('Hour', [FBXFileProperty('I', now.hour)])
    n1_4_6 = FBXFileNode('Minute', [FBXFileProperty('I', now.minute)])
    n1_4_7 = FBXFileNode('Second', [FBXFileProperty('I', now.second)])
    n1_4_8 = FBXFileNode('Millisecond', [FBXFileProperty('I', now.microsecond)])
    n1_5 = FBXFileNode('Creator', [FBXFileProperty('S', 'Camorph Python Toolkit')])
    n1_4.nnested_nodes = [n1_4_1, n1_4_2, n1_4_3, n1_4_4, n1_4_5, n1_4_6, n1_4_7, n1_4_8]
    n1.nnested_nodes = [n1_1, n1_2, n1_3, n1_4, n1_5]

    # Static FileId
    n_2 = FBXFileNode('FileId', [FBXFileProperty('R', b'(\xb3*\xeb\xb6$\xcc\xc2\xbf\xc8\xb0*\xa9+\xfc\xf1')])

    # Static CreationTime

    n_3 = FBXFileNode('CreationTime', [FBXFileProperty('S', now.strftime("%Y-%d-%m %H:%M:%S:%f"))])

    # Static Creator
    n_4 = FBXFileNode('Creator', [FBXFileProperty('S', 'Camorph Python Toolkit')])

    # Static Global Settings
    n_5 = FBXFileNode('GlobalSettings')
    n_5_1 = FBXFileNode('Version', [FBXFileProperty('I', 1000)])
    n_5_2 = FBXFileNode('Properties70')
    n_5_2_1 = FBXFileNode('P', [FBXFileProperty('S', 'UpAxis'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('I', 2)])
    n_5_2_2 = FBXFileNode('P', [FBXFileProperty('S', 'UpAxisSign'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('I', 1)])
    n_5_2_3 = FBXFileNode('P', [FBXFileProperty('S', 'FrontAxis'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('I', 1)])
    n_5_2_4 = FBXFileNode('P', [FBXFileProperty('S', 'FrontAxisSign'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('I', -1)])
    n_5_2_5 = FBXFileNode('P', [FBXFileProperty('S', 'CoordAxis'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('I', 0)])
    n_5_2_6 = FBXFileNode('P', [FBXFileProperty('S', 'CoordAxisSign'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('I', 1)])
    n_5_2_7 = FBXFileNode('P', [FBXFileProperty('S', 'UnitScaleFactor'),
                                FBXFileProperty('S', 'double'),
                                FBXFileProperty('S', 'Number'),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('D', 1.0)])

    n_5_2.nnested_nodes = [n_5_2_1, n_5_2_2, n_5_2_3, n_5_2_4, n_5_2_5, n_5_2_6, n_5_2_7]
    n_5.nnested_nodes = [n_5_1, n_5_2]

    # Static Documents
    n_6 = FBXFileNode('Documents')
    n_6_1 = FBXFileNode('Count',[FBXFileProperty('I',1)])
    n_6_2 = FBXFileNode('Document',[FBXFileProperty('L', 721103447),
                                    FBXFileProperty('S', 'Scene'),
                                    FBXFileProperty('S', 'Scene')])
    n_6_2_1 = FBXFileNode('Properties70')
    n_6_2_1_1 = FBXFileNode('P', [FBXFileProperty('S', 'SourceObject'),
                                FBXFileProperty('S', 'object'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('S', "")])
    n_6_2_1_2 = FBXFileNode('P', [FBXFileProperty('S', 'ActiveAnimStackName'),
                                FBXFileProperty('S', 'KString'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('S', ""),
                                FBXFileProperty('S', "")])
    n_6_2_2 = FBXFileNode('RootNode',[FBXFileProperty('L',0)])
    n_6_2_1.nnested_nodes = [n_6_2_1_1, n_6_2_1_2]
    n_6_2.nnested_nodes = [n_6_2_1, n_6_2_2]
    n_6.nnested_nodes = [n_6_1, n_6_2]

    # Static References
    n_7 = FBXFileNode('References')

    # Definitions
    n_8 = FBXFileNode('Definitions')
    n_8_1 = FBXFileNode('Version', [FBXFileProperty('I', 100)])
    n_8_2 = FBXFileNode('Count', [FBXFileProperty('I', 3)])
    n_8_3 = FBXFileNode('ObjectType', [FBXFileProperty('S', 'GlobalSettings')])
    n_8_3_1 = FBXFileNode('Count', [FBXFileProperty('I', 1)])
    n_8_3.nnested_nodes = [n_8_3_1]
    n_8_4 = FBXFileNode('ObjectType', [FBXFileProperty('S', 'NodeAttribute')])
    n_8_4_1 = FBXFileNode('Count', [FBXFileProperty('I', len(cams))])
    n_8_4_2 = FBXFileNode('PropertyTemplate', [FBXFileProperty('S', 'FbxCamera')])
    n_8_4.nnested_nodes = [n_8_4_1, n_8_4_2]
    n_8_4_2_1 = FBXFileNode('Properties70')
    n_8_4_2.nnested_nodes = [n_8_4_2_1]
    n_8_4_2_1_1 = FBXFileNode('P', [FBXFileProperty('S', 'Position'),
                                    FBXFileProperty('S', 'Vector'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_2 = FBXFileNode('P', [FBXFileProperty('S', 'UpVector'),
                                    FBXFileProperty('S', 'Vector'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 1.0),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_3 = FBXFileNode('P', [FBXFileProperty('S', 'FocalLength'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 34.89327621672628)])
    n_8_4_2_1_4 = FBXFileNode('P', [FBXFileProperty('S', 'AspectWidth'),
                                    FBXFileProperty('S', 'double'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('D', 320.0)])
    n_8_4_2_1_5 = FBXFileNode('P', [FBXFileProperty('S', 'AspectHeight'),
                                    FBXFileProperty('S', 'double'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('D', 200.0)])
    n_8_4_2_1_6 = FBXFileNode('P', [FBXFileProperty('S', 'OpticalCenterX'),
                                    FBXFileProperty('S', 'OpticalCenterX'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_7 = FBXFileNode('P', [FBXFileProperty('S', 'OpticalCenterY'),
                                    FBXFileProperty('S', 'OpticalCenterY'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_8 = FBXFileNode('P', [FBXFileProperty('S', 'FrontPlaneOffsetX'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_9 = FBXFileNode('P', [FBXFileProperty('S', 'FrontPlaneOffsetY'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_8 = FBXFileNode('P', [FBXFileProperty('S', 'FilmOffsetX'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_9 = FBXFileNode('P', [FBXFileProperty('S', 'FilmOffsetY'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0)])
    n_8_4_2_1_10 = FBXFileNode('P', [FBXFileProperty('S', 'FilmWidth'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('D', 0.816)])
    n_8_4_2_1_11 = FBXFileNode('P', [FBXFileProperty('S', 'FilmHeight'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('D', 0.612)])
    n_8_4_2_1_12 = FBXFileNode('P', [FBXFileProperty('S', 'CameraProjectionType'),
                                    FBXFileProperty('S', 'enum'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('I', 0)])
    n_8_4_2_1.nnested_nodes = [n_8_4_2_1_1, n_8_4_2_1_2, n_8_4_2_1_3, n_8_4_2_1_4, n_8_4_2_1_5, n_8_4_2_1_6,
                               n_8_4_2_1_7, n_8_4_2_1_8, n_8_4_2_1_9, n_8_4_2_1_10, n_8_4_2_1_11, n_8_4_2_1_12]
    n_8_5 = FBXFileNode('ObjectType', [FBXFileProperty('S', 'Model')])
    n_8_5_1 = FBXFileNode('Count', [FBXFileProperty('I', len(cams))])
    n_8_5_2 = FBXFileNode('PropertyTemplate', [FBXFileProperty('S', "FbxNode")])
    n_8_5.nnested_nodes = [n_8_5_1, n_8_5_2]
    n_8_5_2_1 = FBXFileNode('Properties70')
    n_8_5_2.nnested_nodes = [n_8_5_2_1]
    n_8_5_2_1_1 = FBXFileNode('P', [FBXFileProperty('S', 'Lcl Translation'),
                                    FBXFileProperty('S', 'Lcl Translation'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 0.0)])
    n_8_5_2_1_2 = FBXFileNode('P', [FBXFileProperty('S', 'Lcl Rotation'),
                                    FBXFileProperty('S', 'Lcl Rotation'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 0.0),
                                    FBXFileProperty('D', 0.0)])
    n_8_5_2_1_3 = FBXFileNode('P', [FBXFileProperty('S', 'Lcl Scaling'),
                                    FBXFileProperty('S', 'Lcl Scaling'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', 100.0),
                                    FBXFileProperty('D', 100.0),
                                    FBXFileProperty('D', 100.0)])
    n_8_5_2_1_4 = FBXFileNode('P', [FBXFileProperty('S', 'RotationOrder'),
                                    FBXFileProperty('S', 'enum'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('I', 0)])
    n_8_5_2_1.nnested_nodes = [n_8_5_2_1_1, n_8_5_2_1_2, n_8_5_2_1_3, n_8_5_2_1_4]
    n_8.nnested_nodes = [n_8_1, n_8_2, n_8_3, n_8_4, n_8_5]

    # Objects
    n_9 = FBXFileNode('Objects')
    cam_property_ids = []
    cam_model_ids = []
    for cam in cams:

        cam.t, cam.r = mu.convert_coordinate_systems(['-y','x', 'z'], cam.t, cam.r, tdir=[1,0,0])

        # Build camera property
        uid = random.randint(1,4294967296)
        cam_property_ids.append(uid)
        build_camera_property_node(cam,uid)
        n_9.nnested_nodes.append(build_camera_property_node(cam, uid))

        # Build camera Model
        uid = random.randint(1, 4294967296)
        cam_model_ids.append(uid)
        n_9.nnested_nodes.append(build_camera_model_node(cam, uid))

    # Connections
    n_10 = FBXFileNode('Connections')
    for idx, _ in enumerate(cam_model_ids):
        n_10.nnested_nodes.extend(build_camera_connections(cam_property_ids[idx], cam_model_ids[idx]))

    # Static Takes
    n_11 = FBXFileNode('Takes')

    file += add_nodes([n1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, n_9, n_10, n_11])

    file += get_footer()

    return file

def build_camera_property_node(cam: Camera, uid:int):

    n_1 = FBXFileNode('NodeAttribute', [FBXFileProperty('L', uid),
                                          FBXFileProperty('S', (bfw.get_string(cam.name) + b'\x00\x01' + b'NodeAttribute').decode(
                                              'Ascii')),
                                          FBXFileProperty('S', "Camera")])
    n_1_1 = FBXFileNode('Properties70')
    n_1_1_1 = FBXFileNode('P', [FBXFileProperty('S', 'Position'),
                                  FBXFileProperty('S', 'Vector'),
                                  FBXFileProperty('S', ''),
                                  FBXFileProperty('S', 'A'),
                                  FBXFileProperty('D', cam.t[0] * 100),
                                  FBXFileProperty('D', cam.t[1] * 100),
                                  FBXFileProperty('D', cam.t[2] * 100)])
    n_1_1_2 = FBXFileNode('P', [FBXFileProperty('S', 'UpVector'),
                                  FBXFileProperty('S', 'Vector'),
                                  FBXFileProperty('S', ''),
                                  FBXFileProperty('S', 'A'),
                                  FBXFileProperty('D', 0.0),
                                  FBXFileProperty('D', 1.0),
                                  FBXFileProperty('D', 0.0)])
    if cam.resolution is not None:
        res = cam.resolution
    else:
        res = (1920,1080)
    n_1_1_3 = FBXFileNode('P', [FBXFileProperty('S', 'AspectWidth'),
                                FBXFileProperty('S', 'double'),
                                FBXFileProperty('S', 'Number'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('D', res[0])])
    n_1_1_4 = FBXFileNode('P', [FBXFileProperty('S', 'AspectHeight'),
                                FBXFileProperty('S', 'double'),
                                FBXFileProperty('S', 'Number'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('D', res[1])])
    if cam.sensor_size is not None:
        sensor_size = cam.sensor_size
    else:
        sensor_size = (36,24)
    n_1_1_5 = FBXFileNode('P', [FBXFileProperty('S', 'FilmWidth'),
                                FBXFileProperty('S', 'double'),
                                FBXFileProperty('S', 'Number'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('D', math_utils.mm_to_inch(sensor_size[0]))])
    n_1_1_6 = FBXFileNode('P', [FBXFileProperty('S', 'FilmHeight'),
                                FBXFileProperty('S', 'double'),
                                FBXFileProperty('S', 'Number'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('D', math_utils.mm_to_inch(sensor_size[1]))])
    if cam.focal_length_mm is not None:
        focal_length = cam.focal_length_mm[0]
    else:
        focal_length = 50
    n_1_1_7 = FBXFileNode('P', [FBXFileProperty('S', 'FocalLength'),
                                FBXFileProperty('S', 'double'),
                                FBXFileProperty('S', 'Number'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('D', focal_length)])
    # principal point
    n_1_1_8 = FBXFileNode('P', [FBXFileProperty('S', 'FilmOffsetX'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', mu.mm_to_inch(cam.lens_shift[0] * 36))])
    n_1_1_9 = FBXFileNode('P', [FBXFileProperty('S', 'FilmOffsetY'),
                                    FBXFileProperty('S', 'Number'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', 'A'),
                                    FBXFileProperty('D', mu.mm_to_inch(cam.lens_shift[1] * 36))])
    n_1_1.nnested_nodes = [n_1_1_1, n_1_1_2, n_1_1_3, n_1_1_4, n_1_1_5, n_1_1_6, n_1_1_7, n_1_1_8, n_1_1_9]
    n_1_2 = FBXFileNode('TypeFlags', [FBXFileProperty('S', 'Camera')])
    n_1_3 = FBXFileNode('GeometryVersion', [FBXFileProperty('I', 124)])
    n_1_4 = FBXFileNode('Position', [FBXFileProperty('D', cam.t[0] * 100),
                                       FBXFileProperty('D', cam.t[1] * 100),
                                       FBXFileProperty('D', cam.t[2] * 100)])
    n_1_5 = FBXFileNode('Up', [FBXFileProperty('D', 0.0),
                                 FBXFileProperty('D', 1.0),
                                 FBXFileProperty('D', 0.0)])

    lookat_vector = cam.r.rotate([1,0,0])
    n_1_6 = FBXFileNode('LookAt', [FBXFileProperty('D', lookat_vector[0]),
                                     FBXFileProperty('D', lookat_vector[1]),
                                     FBXFileProperty('D', lookat_vector[2])])
    n_1.nnested_nodes = [n_1_1, n_1_2, n_1_3, n_1_4, n_1_5, n_1_6]

    return n_1

def build_camera_model_node(cam:Camera, uid:int):
    angles = mu.quaternion_to_euler(cam.r)
    n_1 = FBXFileNode('Model', [FBXFileProperty('L', uid),
                                  FBXFileProperty('S', (bfw.get_string(cam.name) + b'\x00\x01' + b'Model').decode('Ascii')),
                                  FBXFileProperty('S', "Camera")])
    n_1_1 = FBXFileNode('Version', [FBXFileProperty('I', 232)])
    n_1_2 = FBXFileNode('Properties70')
    n_1_2_1 = FBXFileNode('P', [FBXFileProperty('S', 'Lcl Translation'),
                                  FBXFileProperty('S', 'Lcl Translation'),
                                  FBXFileProperty('S', ''),
                                  FBXFileProperty('S', 'A'),
                                  FBXFileProperty('D', cam.t[0] * 100),
                                  FBXFileProperty('D', cam.t[1] * 100),
                                  FBXFileProperty('D', cam.t[2] * 100)])
    n_1_2_2 = FBXFileNode('P', [FBXFileProperty('S', 'Lcl Rotation'),
                                  FBXFileProperty('S', 'Lcl Rotation'),
                                  FBXFileProperty('S', ''),
                                  FBXFileProperty('S', 'A'),
                                  FBXFileProperty('D', angles[0]),
                                  FBXFileProperty('D', angles[1]),
                                  FBXFileProperty('D', angles[2])])
    n_1_2_3 = FBXFileNode('P', [FBXFileProperty('S', 'Lcl Scaling'),
                                  FBXFileProperty('S', 'Lcl Scaling'),
                                  FBXFileProperty('S', ''),
                                  FBXFileProperty('S', 'A'),
                                  FBXFileProperty('D', 100.0),
                                  FBXFileProperty('D', 100.0),
                                  FBXFileProperty('D', 100.0)])
    n_1_2_4 = FBXFileNode('P', [FBXFileProperty('S', 'RotationOrder'),
                                    FBXFileProperty('S', 'enum'),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('S', ''),
                                    FBXFileProperty('I', 0)])
    n_1_2_5 = FBXFileNode('P', [FBXFileProperty('S', 'DefaultAttributeIndex'),
                                FBXFileProperty('S', 'int'),
                                FBXFileProperty('S', 'Integer'),
                                FBXFileProperty('S', ''),
                                FBXFileProperty('I', 0)])
    n_1_2.nnested_nodes = [n_1_2_1, n_1_2_2, n_1_2_3, n_1_2_4, n_1_2_5]
    n_1.nnested_nodes = [n_1_1, n_1_2]

    return n_1

def build_camera_connections(cam_property: int, cam_model: int):
    n_1 = FBXFileNode('C', [FBXFileProperty('S', 'OO'),
                               FBXFileProperty('L', cam_model),
                               FBXFileProperty('L', 0)])
    n_2 = FBXFileNode('C', [FBXFileProperty('S', 'OO'),
                               FBXFileProperty('L', cam_property),
                               FBXFileProperty('L', cam_model)])
    return [n_1,n_2]

def add_property(prop) -> (bytes, int):
    property_type = prop.ptype
    offset = 1
    offset += type_lengths[property_type](prop.pvalue)
    value = bfw.get_string(property_type)
    if property_type in primitive_types.keys():
        value = value + primitive_types[property_type](prop.pvalue)
    elif property_type in complex_types.keys():
        value += bfw.get_uint32(len(prop.pvalue))
        offset += 4
        value = value + complex_types[property_type](prop.pvalue)
    else:
        raise Exception("Unknown property type")

    return value, offset


def get_header() -> bytes:
    # Header is static
    return b'Kaydara FBX Binary  \x00\x1a\x00\xe8\x1c\x00\x00'


def get_footer() -> bytes:
    # Footer is static and magic
    return b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xbc\xab\t\xd0\xc8\xd4f\xb1v\xfb\x83\x1c\xf7&~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8Z\x8cj\xde\xf5\xd9~\xec\xe9\x0c\xe3u\x8f)\x0b'


def add_nodes(nodes):
    value = b''
    # skip header
    offset = 27
    for node in nodes:
        nvalue, offset = add_node_rec(offset, node)
        value += nvalue

    return value


def add_node_rec(offset, nnode) -> bytes:
    properties = nnode.nproperties
    name = nnode.nname
    nested_nodes = nnode.nnested_nodes

    # length of name
    value = bfw.get_uint8(len(name))

    # name
    value += bfw.get_string(name)

    # set offset after known header
    offset += 13 + len(name)

    proplength = 0
    for prop in properties:
        (pvalue, poffset) = add_property(prop)
        proplength += poffset
        value += pvalue
        offset += poffset

    # handle nested nodes

    if len(nested_nodes) > 0:
        nested_offset = offset
        for node in nested_nodes:
            nvalue, noffset = add_node_rec(nested_offset, node)
            nested_offset = noffset
            value += nvalue
        value += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        offset = nested_offset + 13

    # write offset, number of properties and property list length to start of this node
    value = bfw.get_uint32(offset) + bfw.get_uint32(len(properties)) + bfw.get_uint32(proplength) + value

    return value, offset


class FBXFileProperty:
    def __init__(self, ptype: str = "", pvalue: Union[str, int, bool, bytes, float] = None):
        self.ptype: str = ptype
        self.pvalue: Union[str, int, bool, bytes, float] = pvalue


class FBXFileNode:
    def __init__(self, nname: str = '', nproperties=None, nnested_nodes=None):
        if nproperties is None:
            nproperties = []
        if nnested_nodes is None:
            nnested_nodes = []
        self.nproperties = nproperties
        self.nname = nname
        self.nnested_nodes = nnested_nodes
