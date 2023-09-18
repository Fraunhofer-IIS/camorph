import json
import random

from ..model.sfm import sfm, sfm_view, sfm_transform, sfm_pose, sfm_intrinsics
from model.Camera import Camera


def build_file(cams: list[Camera]):
    sfm_json = sfm()

    for cam in cams:
        view = sfm_view()
        view.viewId = str(random.randint(0,65535))
        view.poseId = view.viewId
        view.intrinsicId = str(random.randint(0, 65535))
        view.resectionId = str(random.randint(0, 65536))
        view.path = str(cam.source_image)
        view.width = str(int(cam.resolution[0]))
        view.height = str(int(cam.resolution[1]))

        intrinsic = sfm_intrinsics()
        intrinsic['intrinsicId'] = str(view.intrinsicId)
        intrinsic['width'] = str(int(view.width))
        intrinsic['height'] = str(int(view.height))
        intrinsic['sensorWidth'] = str(cam.sensor_size[0])
        intrinsic['sensorHeight'] = str(cam.sensor_size[1])
        intrinsic['serialNumber'] = str(-1)
        intrinsic['pxFocalLength'] = str(cam.focal_length_px[0])
        intrinsic['pxInitialFocalLength'] = str(cam.focal_length_px[0])
        
        # To also support newer Meshroom version
        intrinsic['focalLength'] = str(cam.focal_length_mm[0])
        intrinsic['initialFocalLength'] = str(cam.focal_length_mm[0])

        intrinsic['type'] = cam.model
        if cam.model == 'radial3' and cam.radial_distortion is not None:
            intrinsic['distortionParams'] = [str(item) for item in cam.radial_distortion]
        intrinsic['principalPoint'] = [str(item) for item in cam.principal_point]

        pose = sfm_pose()
        pose.poseId = view.poseId
        pose.pose.transform['rotation'] = [str(item) for sublist in cam.r.rotation_matrix.tolist() for item in sublist]
        pose.pose.transform['center'] = [str(item) for item in cam.t.tolist()]

        sfm_json.views.append(view)
        sfm_json.poses.append(pose)
        sfm_json.intrinsics.append(intrinsic)

    return json.dumps(sfm_json.__dict__, default=lambda o: o.__dict__, indent=4)