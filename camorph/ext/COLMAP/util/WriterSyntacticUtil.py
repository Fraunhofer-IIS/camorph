import os

from model.Camera import Camera
from utils import math_utils
from utils.file_utils import fixed_list
from utils import bin_writer_utils as bfw


def write_cameras_file_txt(camera_array: list[Camera], output_path):
    num_of_cams = len(camera_array)

    cam_content = [
        "# Camera list with one line of data per camera:",
        "# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]",
        "# Number of cameras: " + str(num_of_cams),
    ]

    for idx, cam in enumerate(camera_array):
        camtype, params = _get_model_and_params(cam, 'txt', str)

        columns = [
            str(idx + 1),  # camera index
            camtype,  # camera type
            str(int(cam.resolution[0])),  # resolution x
            str(int(cam.resolution[1])),  # resolution y
        ]
        columns.extend(params)
        cam_content.append(' '.join(columns))

    camera_file = os.path.join(output_path, "cameras.txt")
    with open(camera_file, "w+") as file:
        for line in cam_content:
            file.write(line + "\n")


def write_cameras_file_bin(camera_array, output_path):
    file = []
    file.append(bfw.get_uint64(len(camera_array)))
    for idx, cam in enumerate(camera_array):
        camtype, params = _get_model_and_params(cam, 'bin', bfw.get_float64)
        file.append(bfw.get_int32(idx+1))
        file.append(bfw.get_int32(camtype))
        file.append(bfw.get_uint64(int(cam.resolution[0])))
        file.append(bfw.get_uint64(int(cam.resolution[1])))
        file.extend(params)
    cameras_file = os.path.join(output_path, "cameras.bin")
    with open(cameras_file, 'wb') as f:
        f.write(b''.join(file))


def write_images_file_txt(camera_array, output_path):
    num_of_cams = len(camera_array)

    images_content = [
        "# Image list with two lines of data per image:",
        "# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME",
        "# POINTS2D[] as (X, Y, POINT3D_ID)",
        "# Number of images: " + str(num_of_cams) + ", mean observation per image: N/A",
    ]

    for idx, cam in enumerate(camera_array):
        # transform camera location/orientation into COLMAP convention
        t_cam_colmap, q_cam_colmap = math_utils.convert_coordinate_systems(['z', '-x', '-y'], cam.t, cam.r,
                                                                          tdir=[0, 0, 1],
                                                                          tup=[0, -1, 0])
        q_cam_colmap = q_cam_colmap.inverse
        t_cam_colmap = -q_cam_colmap.rotate(t_cam_colmap)

        columns = [
            str(idx + 1),
            str(q_cam_colmap[0]),  # QW
            str(q_cam_colmap[1]),  # QX
            str(q_cam_colmap[2]),  # QY
            str(q_cam_colmap[3]),  # QZ
            str(t_cam_colmap[0]),  # TX
            str(t_cam_colmap[1]),  # TY
            str(t_cam_colmap[2]),  # TZ
            str(idx + 1),  # CAM_ID
            cam.source_image,  # Because of crucial_property we know this exists
        ]
        images_content.append(' '.join(columns))
        images_content.append('0 0 -1')
    images_file = os.path.join(output_path, "images.txt")
    with open(images_file, "w+") as file:
        for line in images_content:
            file.write(line + "\n")


def write_images_file_bin(camera_array, output_path):
    file = []
    file.append(bfw.get_uint64(len(camera_array)))
    for idx, cam in enumerate(camera_array):
        t_cam_colmap, q_cam_colmap = math_utils.convert_coordinate_systems(['z', '-x', '-y'], cam.t, cam.r,
                                                                           tdir=[0, 0, 1],
                                                                           tup=[0, -1, 0])
        q_cam_colmap = q_cam_colmap.inverse
        t_cam_colmap = -q_cam_colmap.rotate(t_cam_colmap)
        file.append(bfw.get_int32(idx+1))
        file.extend([bfw.get_float64(x) for x in q_cam_colmap])
        file.extend([bfw.get_float64(x) for x in t_cam_colmap])
        file.append(bfw.get_int32(idx+1))
        file.append(bfw.get_string(cam.source_image))
        file.append(b'\x00')
        file.append(bfw.get_uint64(1))
        file.append(bfw.get_float64(0))
        file.append(bfw.get_float64(0))
        file.append(bfw.get_uint64(0))
    images_file = os.path.join(output_path, "images.bin")
    with open(images_file, 'wb') as f:
        f.write(b''.join(file))

def _get_model_and_params(cam, file_type, func):
    if cam.model == 'pinhole':
        if abs(cam.focal_length_px[0] - cam.focal_length_px[1]) < 0.001:
            camtype = "SIMPLE_PINHOLE" if file_type == 'txt' else 0
            params = [func(cam.focal_length_px[0]), func(cam.principal_point[0]), func(cam.principal_point[1])]
        else:
            camtype = "PINHOLE" if file_type == 'txt' else 1
            params = [func(cam.focal_length_px[0]),func(cam.focal_length_px[1]), func(cam.principal_point[0]), func(cam.principal_point[1])]
    elif cam.model == 'brown':
        if len(cam.radial_distortion) == 1 and (cam.tangential_distortion is None or (cam.tangential_distortion) == 0):
            camtype = "SIMPLE_RADIAL" if file_type == 'txt' else 2
            params = [func(cam.focal_length_px[0]), func(cam.principal_point[0]),
                      func(cam.principal_point[1]), func(cam.radial_distortion[0])]
        elif len(cam.radial_distortion) == 2 and (cam.tangential_distortion is None or (cam.tangential_distortion) == 0):
            camtype = "RADIAL" if file_type == 'txt' else 3
            params = [func(cam.focal_length_px[0]), func(cam.principal_point[0]), func(cam.principal_point[1]),
                      func(cam.radial_distortion[0]), func(cam.radial_distortion[1])]
        elif len(cam.radial_distortion) == 2 and len(cam.tangential_distortion) == 1:
            camtype = "OPENCV" if file_type == 'txt' else 4
            params = [func(cam.focal_length_px[0]), func(cam.focal_length_px[1]), func(cam.principal_point[0]), func(cam.principal_point[1])]
            params.extend([func(x) for x in fixed_list(cam.radial_distortion, 2, float)])
            params.append(func(cam.tangential_distortion[0]))
            params.append("0")
        elif len(cam.radial_distortion) == 2 and len(cam.tangential_distortion) == 2:
            camtype = "OPENCV" if file_type == 'txt' else 4
            params = [func(cam.focal_length_px[0]),func(cam.focal_length_px[1]), func(cam.principal_point[0]), func(cam.principal_point[1])]
            params.extend([func(x) for x in fixed_list(cam.radial_distortion, 2, float)])
            params.extend([func(x) for x in fixed_list(cam.tangential_distortion, 2, float)])
        elif len(cam.radial_distortion) > 2:
            # fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, k5, k6
            camtype = "FULL_OPENCV" if file_type == 'txt' else 12
            params = [func(cam.focal_length_px[0]), func(cam.focal_length_px[1]), func(cam.principal_point[0]), func(cam.principal_point[1])]
            params.append(func(cam.radial_distortion[0]))
            params.append(func(cam.radial_distortion[1]))
            params.append(func(cam.tangential_distortion[0]) if cam.tangential_distortion is not None else "0")
            params.append(func(cam.tangential_distortion[1]) if cam.tangential_distortion is not None and len(cam.tangential_distortion) > 1 else "0")
            params.append(func(cam.radial_distortion[2]) if len(cam.radial_distortion) > 2 else "0")
            params.append(func(cam.radial_distortion[3]) if len(cam.radial_distortion) > 3 else "0")
            params.append(func(cam.radial_distortion[4]) if len(cam.radial_distortion) > 4 else "0")
            params.append(func(cam.radial_distortion[5]) if len(cam.radial_distortion) > 5 else "0")
        else:
            raise Exception(f"Unsupported Camera Model")
    elif cam.model == 'opencv_fisheye':
        if len(cam.radial_distortion) == 1:
            camtype = "SIMPLE_RADIAL_FISHEYE" if file_type == 'txt' else 8
            params = [func(cam.focal_length_px[0]), func(cam.principal_point[0]), func(cam.principal_point[1]),
                      func(cam.radial_distortion[0])]
        elif len(cam.radial_distortion) == 2:
            camtype = "RADIAL_FISHEYE" if file_type == 'txt' else 9
            params = [func(cam.focal_length_px[0]), func(cam.principal_point[0]), func(cam.principal_point[1]),
                      func(cam.radial_distortion[0]), func(cam.radial_distortion[1])]
        else:
            camtype = "OPENCV_FISHEYE" if file_type == 'txt' else 5
            params = [func(cam.focal_length_px[0]), func(cam.principal_point[0]), func(cam.principal_point[1])]
            params.extend([func(x) for x in fixed_list(cam.radial_distortion, 4)])
    else:
        raise Exception(f"Unsupported Camera Model ${cam.model}")

    return camtype, params
