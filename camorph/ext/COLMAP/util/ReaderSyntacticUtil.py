from pyquaternion import Quaternion
import numpy as np
import struct

from camorph.lib.utils.file_utils import extension
from ..model import *
from ..model.CameraModel import CameraModel, CAMERA_MODEL_IDS


# from https://github.com/colmap/colmap/blob/1a4d0bad2e90aa65ce997c9d1779518eaed998d5/scripts/python/read_write_model.py
def read_next_bytes(fid, num_bytes, format_char_sequence, endian_character="<"):
    """Read and unpack the next bytes from a binary file.
    :param fid:
    :param num_bytes: Sum of combination of {2, 4, 8}, e.g. 2, 6, 16, 30, etc.
    :param format_char_sequence: List of {c, e, f, d, h, H, i, I, l, L, q, Q}.
    :param endian_character: Any of {@, =, <, >, !}
    :return: Tuple of read and unpacked values.
    """
    data = fid.read(num_bytes)
    return struct.unpack(endian_character + format_char_sequence, data)




def read_images_txt(path):
    with open(path, 'r') as f:
        img_arr = []
        for x in f:
            if x[0] != '#':
                #   IMAGE_ID QW QX QY QZ TX TY TZ CAMERA_ID NAME
                pars = x.split(' ')
                img_id = int(pars[0])
                rot = Quaternion(float(pars[1]), float(pars[2]), float(pars[3]), float(pars[4]))
                t = np.asarray([float(pars[5]), float(pars[6]), float(pars[7])])
                cam_id = int(pars[8])
                name = pars[9]
                name = name.replace('\n','')
                # ignore features
                f.readline()
                img_arr.append(ColmapImage(img_id, rot, t, cam_id, name))
    return img_arr

# from https://github.com/colmap/colmap/blob/1a4d0bad2e90aa65ce997c9d1779518eaed998d5/scripts/python/read_write_model.py
def read_images_bin(path_to_model_file: str):
    img_arr = []
    with open(path_to_model_file, "rb") as fid:
        num_reg_images = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_reg_images):
            binary_image_properties = read_next_bytes(
                fid, num_bytes=64, format_char_sequence="idddddddi")
            img_id = binary_image_properties[0]
            rot = np.array(binary_image_properties[1:5])
            rot = Quaternion(rot[0], rot[1], rot[2], rot[3])
            t = np.array(binary_image_properties[5:8])
            cam_id = binary_image_properties[8]
            image_name = ""
            current_char = read_next_bytes(fid, 1, "c")[0]
            while current_char != b"\x00":  # look for the ASCII 0 entry
                image_name += current_char.decode("utf-8")
                current_char = read_next_bytes(fid, 1, "c")[0]
            # ignore stuff wie do not need
            num_points2D = read_next_bytes(fid, num_bytes=8,
                                           format_char_sequence="Q")[0]
            read_next_bytes(fid, num_bytes=24 * num_points2D,
                            format_char_sequence="ddq" * num_points2D)
            img_arr.append(ColmapImage(img_id, rot, t, cam_id, image_name))
    return img_arr


def read_images(path: str):
    return read_images_txt(path) if extension(path) == ".txt" else read_images_bin(path)


def read_cameras_txt(path: str):
    with open(path, 'r') as f:
        cam_arr = []
        for x in f:
            if x[0] != '#':
                pars = x.replace('\n','').split(' ')
                cam_arr.append(ColmapCamera(int(pars[0]), pars[1], (int(pars[2]), int(pars[3])), pars[4:]))

        return cam_arr


# from https://github.com/colmap/colmap/blob/1a4d0bad2e90aa65ce997c9d1779518eaed998d5/scripts/python/read_write_model.py
def read_cameras_bin(path_to_model_file):
    cam_arr = []
    with open(path_to_model_file, "rb") as fid:
        num_cameras = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_cameras):
            camera_properties = read_next_bytes(
                fid, num_bytes=24, format_char_sequence="iiQQ")
            camera_id = camera_properties[0]
            model_id = camera_properties[1]
            model_name = CAMERA_MODEL_IDS[camera_properties[1]].model_name
            width = camera_properties[2]
            height = camera_properties[3]
            num_params = CAMERA_MODEL_IDS[model_id].num_params
            params = read_next_bytes(fid, num_bytes=8 * num_params,
                                     format_char_sequence="d" * num_params)
            cam_arr.append(ColmapCamera(camera_id, model_name, (width, height), params))
    return cam_arr


def read_cameras(path: str):
    return read_cameras_txt(path) if extension(path) == ".txt" else read_cameras_bin(path)
