import json
import re
import os
from os.path import basename

import numpy as np
from pyquaternion import Quaternion

from model.Camera import Camera
from utils import math_utils



def read_sfm(input_path):
    with open(input_path, 'r') as f:
        sfm_json = json.loads(f.read())
        poses = sfm_json['poses']
        intrinsics = sfm_json['intrinsics']
        cams = []
        for view in sfm_json['views']:
            pose = next((p for p in poses if p['poseId'] == view['poseId']), None)
            intrinsic = next((i for i in intrinsics if i['intrinsicId'] == view['intrinsicId']), None)
            if pose is not None and intrinsic is not None:
                transform = pose['pose']['transform']
                cam = Camera()
                cam.name = basename(view['path']).split('.')[0]
                cam.projection_type = 'perspective'
                cam.t = np.asarray([float(x) for x in transform['center']])
                rotmat = np.asarray([float(x) for x in transform['rotation']]).reshape((3,3))
                cam.r = Quaternion(matrix = rotmat)
                cam.focal_length_px = [float(intrinsic['pxFocalLength']),float(intrinsic['pxFocalLength'])]
                cam.projection_type = 'perspective'
                cam.resolution = (float(view['width']), float(view['height']))
                cam.principal_point = tuple([float(x) for x in intrinsic['principalPoint']])
                cam.sensor_size = (float(intrinsic['sensorWidth']), float(intrinsic['sensorHeight']))
                cam.model = intrinsic['type']
                if 'distortionParams' in intrinsic:
                    cam.model = 'brown'
                    cam.radial_distortion = [float(x) for x in intrinsic['distortionParams']]
                else:
                    cam.model = 'pinhole'
                cam.source_image = re.sub('/', os.path.sep, view['path'])
                cams.append(cam)

    return cams
