import json
import re
import os
from os.path import basename

import numpy as np
from pyquaternion import Quaternion
from distutils.version import StrictVersion

from camorph.lib.model.Camera import Camera
from camorph.lib.utils import math_utils



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
                if intrinsic.get('pxFocalLength') is not None:
                    cam.focal_length_px = [float(intrinsic['pxFocalLength']),float(intrinsic['pxFocalLength'])]
                elif intrinsic.get('focalLength') is not None:
                    cam.focal_length_mm = [float(intrinsic['focalLength']),float(intrinsic['focalLength'])]

                cam.projection_type = 'perspective'
                cam.resolution = (float(view['width']), float(view['height']))
                if StrictVersion('.'.join(sfm_json['version'])) > StrictVersion('1.2.0'):
                    cam.principal_point = np.add(tuple([float(x) for x in intrinsic['principalPoint']]),np.multiply(cam.resolution,0.5))
                else:
                    cam.principal_point = tuple([float(x) for x in intrinsic['principalPoint']])
                # Unfortunately, Meshroom sensor size cannot be trusted
                # Calculating based on image aspect ratio
                sensor_size_x = 36.0
                cam.sensor_size = (sensor_size_x, sensor_size_x * (cam.resolution[1]/cam.resolution[0]))
                # cam.sensor_size = (float(intrinsic['sensorWidth']), float(intrinsic['sensorHeight']))
                cam.model = intrinsic['type']
                if 'distortionParams' in intrinsic:
                    cam.model = 'brown'
                    cam.radial_distortion = [float(x) for x in intrinsic['distortionParams']]
                else:
                    cam.model = 'pinhole'
                cam.source_image = view['path']
                cams.append(cam)

    return cams
