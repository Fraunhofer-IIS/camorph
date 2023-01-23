import math
import re
from os import listdir
from os.path import join

import numpy as np
import rdflib
from PIL import Image
from pyquaternion import Quaternion

from utils import math_utils, file_utils
from utils.file_utils import get_files_in_dir
from model.FileHandler import FileHandler
from model.Camera import Camera


class RealityCapture(FileHandler):
    def __init__(self):
        pass

    def crucial_properties(self) -> list[(str, type)]:
        return ['source_image','lens_shift']

    def name(self):
        return "reality_capture"

    def file_number(self):
        return -1

    def read_file(self, input_path: str, **kwargs):
        cams = []
        xmp_files = get_files_in_dir(input_path, '.xmp')
        img_files = [f for f in listdir(input_path) if
                     f[:f.rfind('.')] + '.xmp' in xmp_files and not f.endswith('.xmp')]
        if len(img_files) < len(xmp_files):
            raise Exception("Less images than xmp files in directory.")
        pairs = [(x, y) for (x, y) in zip(sorted(xmp_files), sorted(img_files))]
        for xmp_file, img_file in pairs:
            xmp_filepath = join(input_path, xmp_file)
            img_filepath = join(input_path, img_file)
            with open(xmp_filepath, 'r') as f:
                g = rdflib.Graph()
                data = f.read()
                # need to remove unsupported xmpmeta tag for rdf parser
                data = re.sub("<.*:xmpmeta.*>", "", data)
                g.parse(data=data, format='xml')
                cam_data = dict()
                for _, p, o in g:
                    frag = p.split('#')[1]
                    cam_data[frag] = o

                cam = Camera()
                cam.autocompute = True
                cam.projection_type = 'perspective'
                cam.name = img_file[:img_file.rfind('.')]
                cam.source_image = img_filepath
                with Image.open(img_filepath) as i:
                    cam.resolution = i.size

                cam.t = np.asarray([float(x) for x in cam_data['Position'].value.split(' ')])
                mat = np.asarray([float(x) for x in cam_data['Rotation'].value.split(' ')]).reshape(3, 3)
                cam.r = Quaternion(matrix=mat)
                cam.model = cam_data['DistortionModel'].value
                cam.sensor_size = (36, 24)
                cam.focal_length_mm = [float(cam_data['FocalLength35mm'].value),float(cam_data['FocalLength35mm'].value)]
                cam.lens_shift = (float(cam_data['PrincipalPointU'].value), float(cam_data['PrincipalPointV'].value))
                distortion_coeffs = [float(x) for x in cam_data['DistortionCoeficients'].value.split(' ')]
                if cam.model == 'brown3':
                    cam.model = 'brown'
                    cam.radial_distortion = distortion_coeffs[:3]
                elif cam.model == 'brown4':
                    cam.model = 'brown'
                    cam.radial_distortion = distortion_coeffs[:4]
                elif cam.model == 'brown3t2':
                    cam.model = 'brown'
                    cam.radial_distortion = distortion_coeffs[:3]
                    cam.tangential_distortion = distortion_coeffs[4:]
                elif cam.model == 'brown4t2':
                    cam.model = 'brown'
                    cam.radial_distortion = distortion_coeffs[:4]
                    cam.tangential_distortion = distortion_coeffs[4:]
                elif cam.model == 'division':
                    cam.radial_distortion = distortion_coeffs[0]
                cams.append(cam)
        return self.coordinate_from(cams)

    def write_file(self, camera_array: list[Camera], output_path: str, file_type=None):
        cams = self.coordinate_into(camera_array)
        for cam in cams:
            if cam.model == 'brown':
                if len(cam.radial_distortion) <= 3:
                    if cam.tangential_distortion is not None and len(cam.tangential_distortion) > 1:
                        dist_model = 'brown3t2'
                    else:
                        dist_model = 'brown3'
                elif len(cam.radial_distortion) > 3:
                    if cam.tangential_distortion is not None and len(cam.tangential_distortion) > 1:
                        dist_model = 'brown4t2'
                    else:
                        dist_model = 'brown4'
            elif cam.model == 'division':
                dist_model = 'division'
            else:
                dist_model = 'division'

            dist_coeffs = file_utils.fixed_list(cam.radial_distortion, 4, float)
            dist_coeffs.extend(file_utils.fixed_list(cam.tangential_distortion, 2, float))
            file = f"""<x:xmpmeta xmlns:x="adobe:ns:meta/">
                      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                        <rdf:Description xcr:Version="3" xcr:PosePrior="locked" xcr:Coordinates="absolute"
                           xcr:DistortionModel="{dist_model}" xcr:FocalLength35mm="{cam.focal_length_mm[0]}"
                           xcr:Skew="0" xcr:AspectRatio="1" xcr:PrincipalPointU="{cam.lens_shift[0]}"
                           xcr:PrincipalPointV="{cam.lens_shift[1]}" xcr:CalibrationPrior="exact"
                           xcr:CalibrationGroup="-1" xcr:DistortionGroup="-1" xcr:InTexturing="1"
                           xcr:InMeshing="1" xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
                          <xcr:Rotation>{' '.join([str(x) for x in cam.r.rotation_matrix.flat])}</xcr:Rotation>
                          <xcr:Position>{' '.join([str(x) for x in cam.t])}</xcr:Position>
                          <xcr:DistortionCoeficients>{' '.join([str(x) for x in dist_coeffs])}</xcr:DistortionCoeficients>
                        </rdf:Description>
                      </rdf:RDF>
</x:xmpmeta>
                    """
            target_path = output_path + cam.source_image[cam.source_image.rfind('\\'):cam.source_image.rfind('.')] + '.xmp'
            with open(target_path, 'w') as f:
                f.write(file)

    def coordinate_into(self, camera_array: list[Camera]):
        cam_arr = camera_array.copy()
        for cam in cam_arr:
            # Reality Capture stores the inverse
            cam.t, cam.r = math_utils.convert_coordinate_systems(['x', 'y', 'z'], cam.t, cam.r,
                                                                tdir=[0, 0, 1], tup=[0, -1, 0], transpose=True)
            cam.r = cam.r.inverse

        return cam_arr

    def coordinate_from(self, camera_array: list[Camera]):
        cam_arr = camera_array.copy()
        for cam in cam_arr:
            # Reality Capture stores the inverse
            cam.r = cam.r.inverse
            cam.t, cam.r = math_utils.convert_coordinate_systems(['x', 'y', 'z'], cam.t, cam.r, cdir=[0, 0, 1],
                                                                cup=[0, -1, 0])
        return cam_arr

    def RealityCapture_rotation_matrix(self, y, p, r):
        # This function only serves documentation purposes
        # RealityCapture computes rotation in a different way
        # yaw is around z, pitch around y and roll around x
        # The rotational order is zxy
        # But in the formula below, x and y are swapped
        # Additionally, the x angle is not measure counter-clockwise, but clockwise
        # This means that for example R[1][0] which would normally be cos(x)*sin(z) becomes -cos(y)*sin(z)
        cx = math.cos(math.radians(r))
        cy = math.cos(math.radians(p))
        cz = math.cos(math.radians(y))
        sx = math.sin(math.radians(r))
        sy = math.sin(math.radians(p))
        sz = math.sin(math.radians(y))
        return np.asarray([[cx * cz + sx * sy * sz, -cx * sz + cz * sx * sy, -cy * sx],
                           [-cy * sz, -cy * cz, -sy],
                           [cx * sy * sz - cz * sx, cx * cz * sy + sx * sz, -cx * cy]])
